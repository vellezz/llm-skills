namespace Fixture.Api.Contracts;

/// <summary>A customer order as returned by the API.</summary>
public record OrderDto(Guid Id, string CustomerName, decimal Total, string Status);
