namespace Fixture.Api.Data.Entities;

public enum OrderStatus
{
    New,
    Paid,
    Shipped,
    Cancelled
}

public class Order
{
    public Guid Id { get; set; }
    public string Number { get; set; } = string.Empty;
    public OrderStatus Status { get; set; } = OrderStatus.New;
    public DateTime CreatedAt { get; set; }
    public Guid CustomerId { get; set; }
    public Customer Customer { get; set; } = null!;
    public ICollection<OrderItem> Items { get; set; } = new List<OrderItem>();
}
