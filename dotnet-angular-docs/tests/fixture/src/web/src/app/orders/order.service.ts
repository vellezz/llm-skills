import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Order {
  id: string;
  customerName: string;
  total: number;
  status: string;
}

export interface CreateOrderRequest {
  customerName: string;
  quantity: number;
}

@Injectable({ providedIn: 'root' })
export class OrderService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/orders`;

  getOrders(status?: string, page = 1): Observable<Order[]> {
    const params: Record<string, string | number> = { page };
    if (status) {
      params['status'] = status;
    }
    return this.http.get<Order[]>(this.baseUrl, { params });
  }

  getById(id: string): Observable<Order> {
    return this.http.get<Order>(`${this.baseUrl}/${id}`);
  }

  create(request: CreateOrderRequest): Observable<Order> {
    return this.http.post<Order>(this.baseUrl, request);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
