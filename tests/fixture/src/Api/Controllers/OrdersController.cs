using Fixture.Api.Contracts;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace Fixture.Api.Controllers;

/// <summary>Manages customer orders.</summary>
[ApiController]
[Route("api/[controller]")]
[Authorize]
public class OrdersController : ControllerBase
{
    private static readonly List<OrderDto> Store = new();

    /// <summary>Lists orders, optionally filtered by status.</summary>
    [HttpGet]
    [ProducesResponseType(typeof(List<OrderDto>), StatusCodes.Status200OK)]
    public ActionResult<List<OrderDto>> GetAll([FromQuery] string? status, [FromQuery] int page = 1)
    {
        var result = status is null ? Store : Store.Where(o => o.Status == status).ToList();
        return Ok(result.Skip((page - 1) * 20).Take(20).ToList());
    }

    /// <summary>Gets a single order by its identifier.</summary>
    [HttpGet("{id:guid}")]
    [ProducesResponseType(typeof(OrderDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public ActionResult<OrderDto> GetById(Guid id)
    {
        var order = Store.FirstOrDefault(o => o.Id == id);
        return order is null ? NotFound() : Ok(order);
    }

    /// <summary>Creates a new order.</summary>
    [HttpPost]
    [ProducesResponseType(typeof(OrderDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public ActionResult<OrderDto> Create([FromBody] CreateOrderRequest request)
    {
        var order = new OrderDto(Guid.NewGuid(), request.CustomerName, request.Quantity * 9.99m, "New");
        Store.Add(order);
        return CreatedAtAction(nameof(GetById), new { id = order.Id }, order);
    }

    /// <summary>Deletes an order. Admin only.</summary>
    [HttpDelete("{id:guid}")]
    [Authorize(Roles = "Admin")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public IActionResult Delete(Guid id)
    {
        var removed = Store.RemoveAll(o => o.Id == id) > 0;
        return removed ? NoContent() : NotFound();
    }
}
