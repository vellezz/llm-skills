import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Order, OrderService } from './order.service';

@Component({
  selector: 'app-orders-list',
  standalone: true,
  imports: [RouterLink],
  template: `
    <h1>Orders</h1>
    <a routerLink="/orders/new">New order</a>
    <table>
      <tr *ngFor="let order of orders()">
        <td>{{ order.customerName }}</td>
        <td>{{ order.status }}</td>
        <td>{{ order.total }}</td>
      </tr>
    </table>
  `
})
export class OrdersListComponent {
  private readonly orderService = inject(OrderService);
  readonly orders = signal<Order[]>([]);

  constructor() {
    this.orderService.getOrders().subscribe(o => this.orders.set(o));
  }
}
