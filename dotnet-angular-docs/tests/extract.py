"""Deterministic .NET API-surface extractor.

Computes the ground truth for behavioral tests at runtime, so the harness can
run against ANY provided application sources (--target), not just the fixture.

Handles:
- attribute-routed controllers: class-level [Route("...")] with the
  [controller] token + method-level [HttpGet("...")] etc.
- minimal APIs: app.MapGet("...") and one level of MapGroup prefixing
  (var g = app.MapGroup("/x"); g.MapGet("/y") -> /x/y), including groups
  declared in extension-method files.
- FastEndpoints: verb calls in Configure() — Get(...)/Post(...)/... and the
  Verbs(...)+Routes(...) form — resolving a route argument that is a string
  const declared in the same class (e.g. Get(Route) with
  `const string Route = "/x"`).

Known limits (documented, deterministic): no nested MapGroup chains, no
FastEndpoints Group<T> prefixes, no [ApiVersion] expansion, no routes built
by string concatenation/interpolation. Because the extractor is a best-effort
LOWER BOUND on the surface, target-mode assertions treat it that way:
fabrication (a documented route with no trace in sources) is a hard failure,
while completeness gaps are warnings.
"""
from __future__ import annotations

import re
from pathlib import Path

EXCLUDED_DIRS = {
    "bin", "obj", "node_modules", ".git", "dist", ".angular", ".vs",
    ".idea", "packages", "TestResults", "artifacts",
}

CONTROLLER_CLASS = re.compile(r"\bclass\s+(\w+?)Controller\b")
ROUTE_ATTR = re.compile(r'\[Route\("([^"]*)"\)\]')
HTTP_ATTR = re.compile(r'\[Http(Get|Post|Put|Patch|Delete)(?:\("([^"]*)"\))?\]')

MAP_GROUP = re.compile(r'(\w+)\s*=\s*\w+\.MapGroup\(\s*"([^"]*)"')
MAP_CALL = re.compile(r'(\w+)\.Map(Get|Post|Put|Patch|Delete)\(\s*"([^"]*)"')

# FastEndpoints: string consts and verb/route calls inside Configure()
FE_MARKER = re.compile(r"\bFastEndpoints\b|:\s*Endpoint(WithoutRequest|WithoutResponse|<|\b)")
FE_CONST = re.compile(r'(?:const|static\s+readonly)\s+string\s+(\w+)\s*=\s*"([^"]*)"')
FE_VERB = re.compile(r'(?<![.\w])(Get|Post|Put|Patch|Delete)\s*\(([^;{}]*?)\)')
FE_VERBS = re.compile(r'\bVerbs\s*\(([^;)]*)\)')
FE_ROUTES = re.compile(r'\bRoutes\s*\(([^;)]*)\)')
FE_HTTP = re.compile(r'Http\.(GET|POST|PUT|PATCH|DELETE)')
ARG_LITERAL = re.compile(r'"([^"]*)"')


def _cs_files(root: Path) -> list[Path]:
    files = []
    for p in root.rglob("*.cs"):
        if not any(part in EXCLUDED_DIRS for part in p.parts):
            files.append(p)
    return files


def _join(prefix: str, template: str) -> str:
    parts = [seg for seg in (prefix.strip("/"), template.strip("/")) if seg]
    return "/" + "/".join(parts)


def _from_controllers(text: str) -> set[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    cls = CONTROLLER_CLASS.search(text)
    if not cls:
        return found
    route = ROUTE_ATTR.search(text)
    class_route = route.group(1) if route else ""
    class_route = class_route.replace("[controller]", cls.group(1).lower())
    for m in HTTP_ATTR.finditer(text):
        method = m.group(1).upper()
        template = m.group(2) or ""
        found.add((method, _join(class_route, template)))
    return found


def _from_minimal_apis(text: str) -> set[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    groups = {m.group(1): m.group(2) for m in MAP_GROUP.finditer(text)}
    for m in MAP_CALL.finditer(text):
        receiver, method, template = m.group(1), m.group(2).upper(), m.group(3)
        if receiver == "MapGroup":  # chained app.MapGroup(...).MapGet(...) — unsupported
            continue
        prefix = groups.get(receiver, "")
        found.add((method, _join(prefix, template)))
    return found


def _resolve_route_args(arg_str: str, consts: dict[str, str]) -> list[str]:
    """From a verb-call argument string, resolve route templates: string
    literals verbatim, bare identifiers via the class const map. Ignores
    non-route args (e.g. Get(Route, x => ...)) that don't resolve."""
    routes: list[str] = []
    literals = ARG_LITERAL.findall(arg_str)
    if literals:
        routes.extend(literals)
    # bare identifiers (Get(Route)) — only when no literal already matched them
    for ident in re.findall(r'(?<![".\w])([A-Za-z_]\w*)(?![\w"])', arg_str):
        if ident in consts:
            routes.append(consts[ident])
    return routes


def _from_fastendpoints(text: str) -> set[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    if not FE_MARKER.search(text):
        return found
    consts = {m.group(1): m.group(2) for m in FE_CONST.finditer(text)}

    for m in FE_VERB.finditer(text):
        method = m.group(1).upper()
        for route in _resolve_route_args(m.group(2), consts):
            joined = _join("", route)
            if joined != "/":  # Get("")/Get("/") = group-relative root, not a real path
                found.add((method, joined))

    # Verbs(Http.GET, ...) + Routes("/x", ...) form
    verbs = [g.upper() for m in FE_VERBS.finditer(text) for g in FE_HTTP.findall(m.group(1))]
    if verbs:
        route_args = " , ".join(m.group(1) for m in FE_ROUTES.finditer(text))
        for route in _resolve_route_args(route_args, consts):
            for method in verbs:
                found.add((method, _join("", route)))
    return found


def extract_endpoints(root: Path) -> set[tuple[str, str]]:
    """Return {(METHOD, raw_route)} for all endpoints found under root."""
    found: set[tuple[str, str]] = set()
    for f in _cs_files(root):
        text = f.read_text(encoding="utf-8", errors="replace")
        found |= _from_controllers(text)
        found |= _from_minimal_apis(text)
        found |= _from_fastendpoints(text)
    return found


def sources_blob(root: Path) -> str:
    """All C# sources concatenated — used to soft-verify 'invented' endpoints."""
    return "\n".join(
        f.read_text(encoding="utf-8", errors="replace") for f in _cs_files(root)
    )


if __name__ == "__main__":
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    for method, route in sorted(extract_endpoints(root), key=lambda e: (e[1], e[0])):
        print(f"{method:7} {route}")
