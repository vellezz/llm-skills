import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { OrderService } from './order.service';

@Component({
  selector: 'app-order-form',
  standalone: true,
  imports: [ReactiveFormsModule],
  template: `
    <h1>New order</h1>
    <form [formGroup]="form" (ngSubmit)="save()">
      <label>
        Customer name
        <input formControlName="customerName" />
      </label>
      <label>
        Quantity
        <input type="number" formControlName="quantity" />
      </label>
      <button type="submit" [disabled]="form.invalid">Save</button>
    </form>
  `
})
export class OrderFormComponent {
  private readonly orderService = inject(OrderService);
  private readonly router = inject(Router);

  form = new FormGroup({
    customerName: new FormControl('', [Validators.required, Validators.maxLength(100)]),
    quantity: new FormControl(1, [Validators.required, Validators.min(1), Validators.max(100)])
  });

  save(): void {
    if (this.form.invalid) {
      return;
    }
    this.orderService.create({
      customerName: this.form.value.customerName!,
      quantity: this.form.value.quantity!
    }).subscribe(() => this.router.navigate(['/orders']));
  }
}
