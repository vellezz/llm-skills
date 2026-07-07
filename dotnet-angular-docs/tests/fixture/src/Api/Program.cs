using Fixture.Api.Data;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("Default")));
builder.Services.AddAuthentication();
builder.Services.AddAuthorization();

var app = builder.Build();

// Health probe used by the container orchestrator.
app.MapGet("/api/health", () => Results.Ok(new { status = "ok" })).AllowAnonymous();

app.MapControllers();

app.Run();
