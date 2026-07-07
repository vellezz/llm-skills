import { Routes } from '@angular/router';
import { authGuard } from './auth/auth.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./dashboard/dashboard.component').then(m => m.DashboardComponent),
    title: 'Dashboard'
  },
  {
    path: 'orders',
    canActivate: [authGuard],
    loadComponent: () => import('./orders/orders-list.component').then(m => m.OrdersListComponent),
    title: 'Orders'
  },
  {
    path: 'orders/new',
    canActivate: [authGuard],
    loadComponent: () => import('./orders/order-form.component').then(m => m.OrderFormComponent),
    title: 'New order'
  }
];
