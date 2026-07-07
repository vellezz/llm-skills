using System.ComponentModel.DataAnnotations;

namespace Fixture.Api.Contracts;

/// <summary>Payload for creating a new order.</summary>
public class CreateOrderRequest
{
    [Required]
    [MaxLength(100)]
    public string CustomerName { get; set; } = string.Empty;

    [Range(1, 100)]
    public int Quantity { get; set; } = 1;
}
