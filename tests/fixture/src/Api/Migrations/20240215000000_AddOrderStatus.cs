using Microsoft.EntityFrameworkCore.Migrations;

namespace Fixture.Api.Migrations;

public partial class AddOrderStatus : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.AddColumn<string>(
            name: "Status",
            table: "Orders",
            maxLength: 20,
            nullable: false,
            defaultValue: "New");
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropColumn(name: "Status", table: "Orders");
    }
}
