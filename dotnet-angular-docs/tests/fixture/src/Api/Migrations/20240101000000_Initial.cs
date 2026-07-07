using Microsoft.EntityFrameworkCore.Migrations;

namespace Fixture.Api.Migrations;

public partial class Initial : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.CreateTable(
            name: "Customers",
            columns: table => new
            {
                Id = table.Column<Guid>(nullable: false),
                Name = table.Column<string>(maxLength: 100, nullable: false),
                Email = table.Column<string>(maxLength: 255, nullable: false)
            },
            constraints: table => table.PrimaryKey("PK_Customers", x => x.Id));

        migrationBuilder.CreateTable(
            name: "Orders",
            columns: table => new
            {
                Id = table.Column<Guid>(nullable: false),
                Number = table.Column<string>(maxLength: 20, nullable: false),
                CreatedAt = table.Column<DateTime>(nullable: false),
                CustomerId = table.Column<Guid>(nullable: false)
            },
            constraints: table => table.PrimaryKey("PK_Orders", x => x.Id));

        migrationBuilder.CreateTable(
            name: "OrderItems",
            columns: table => new
            {
                Id = table.Column<Guid>(nullable: false),
                ProductName = table.Column<string>(maxLength: 200, nullable: false),
                Quantity = table.Column<int>(nullable: false),
                UnitPrice = table.Column<decimal>(precision: 18, scale: 2, nullable: false),
                OrderId = table.Column<Guid>(nullable: false)
            },
            constraints: table => table.PrimaryKey("PK_OrderItems", x => x.Id));

        migrationBuilder.CreateIndex(name: "IX_Customers_Email", table: "Customers", column: "Email", unique: true);
        migrationBuilder.CreateIndex(name: "IX_Orders_Number", table: "Orders", column: "Number", unique: true);
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropTable(name: "OrderItems");
        migrationBuilder.DropTable(name: "Orders");
        migrationBuilder.DropTable(name: "Customers");
    }
}
