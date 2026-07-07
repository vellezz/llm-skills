namespace Fixture.Api.Data.Entities;

public class OrderItem
{
    public Guid Id { get; set; }
    public string ProductName { get; set; } = string.Empty;
    public int Quantity { get; set; }
    public decimal UnitPrice { get; set; }
    public Guid OrderId { get; set; }
    public Order Order { get; set; } = null!;
}
