# 🔑 Quick Reference Card

## Test Accounts (After Seeding)

### **Admin Account**
```
Email:    admin@ecommerce.com
Password: Admin123!
Role:     admin
```
**Permissions:** Full access to everything

---

### **Manager Account**
```
Email:    manager@ecommerce.com
Password: Manager123!
Role:     manager
```
**Permissions:** Product management, order management, customer viewing

---

### **Cashier Account**
```
Email:    cashier@ecommerce.com
Password: Cashier123!
Role:     cashier
```
**Permissions:** Order processing, payment updates, basic order viewing

---

### **Customer Accounts**
```
1. john.doe@email.com      / Customer123!
2. jane.smith@email.com    / Customer123!
3. bob.wilson@email.com    / Customer123!
4. alice.brown@email.com   / Customer123!
5. charlie.davis@email.com / Customer123!
```
**Permissions:** Own profile, cart, and orders only

---

## 🔗 API Endpoints Quick Reference

### **Base URL**
```
http://localhost:5000/api
```

### **Authentication**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login | No |
| GET | `/auth/me` | Get current user | Yes |
| POST | `/auth/change-password` | Change password | Yes |
| POST | `/auth/refresh` | Refresh token | Yes (refresh token) |

### **Categories**
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|-----------|
| GET | `/categories` | List all categories | Public |
| GET | `/categories/{id}` | Get category by ID | Public |
| GET | `/categories/slug/{slug}` | Get by slug | Public |
| POST | `/categories` | Create category | Admin |
| POST | `/categories/{id}/subcategory` | Create subcategory | Manager |
| PUT | `/categories/{id}` | Update category | Manager |
| DELETE | `/categories/{id}` | Delete category | Admin |

### **Products**
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|-----------|
| GET | `/products` | List all products | Public |
| GET | `/products/{id}` | Get product by ID | Public |
| GET | `/products/slug/{slug}` | Get by slug | Public |
| GET | `/products/search?barcode=XXX` | Search by barcode | Staff |
| POST | `/products` | Create product | Manager |
| PUT | `/products/{id}` | Update product | Manager |
| PUT | `/products/{id}/stock` | Update stock | Manager |
| DELETE | `/products/{id}` | Delete product | Admin |

### **Cart**
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|-----------|
| GET | `/cart` | Get my cart | Customer |
| POST | `/cart/items` | Add to cart | Customer |
| PUT | `/cart/items/{product_id}` | Update item quantity | Customer |
| DELETE | `/cart/items/{product_id}` | Remove from cart | Customer |
| POST | `/cart/clear` | Clear cart | Customer |
| GET | `/cart/validate` | Validate cart | Customer |

### **Orders**
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|-----------|
| POST | `/orders` | Create order from cart | Customer |
| GET | `/orders` | Get my orders | Customer |
| GET | `/orders/{id}` | Get order by ID | Customer/Staff |
| POST | `/orders/{id}/cancel` | Cancel order | Customer |
| GET | `/orders/today` | Today's orders | Staff |
| GET | `/orders/search?number=XXX` | Search by number | Staff |
| PUT | `/orders/{id}/status` | Update status | Staff |
| PUT | `/orders/{id}/payment-status` | Update payment | Staff |
| POST | `/orders/{id}/ship` | Mark as shipped | Staff |
| GET | `/orders/admin` | All orders | Manager |
| POST | `/orders/{id}/notes` | Add notes | Manager |
| POST | `/orders/{id}/refund` | Process refund | Admin |
| DELETE | `/orders/{id}` | Delete order | Admin |

### **Users**
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|-----------|
| GET | `/users/profile` | Get my profile | Any logged in |
| PUT | `/users/profile` | Update my profile | Any logged in |
| GET | `/users/customers` | List customers | Manager |
| GET | `/users` | List all users | Admin |
| GET | `/users/{id}` | Get user by ID | Admin |
| PUT | `/users/{id}` | Update user | Admin |
| PUT | `/users/{id}/role` | Change role | Admin |
| PUT | `/users/{id}/ban` | Ban/unban user | Admin |
| POST | `/users/{id}/reset-password` | Reset password | Admin |
| GET | `/users/stats` | User statistics | Admin |
| DELETE | `/users/{id}` | Delete user | Admin |

---

## 📝 Enum Values Reference

### **User Roles**
```
- admin      (Full access)
- customer   (Own data only)
- manager    (Products, orders, customers)
- cashier    (Order processing)
```

### **Order Statuses**
```
- pending      (Just created)
- confirmed    (Confirmed by staff)
- processing   (Being prepared)
- shipped      (On the way)
- delivered    (Completed)
- cancelled    (Cancelled)
- refunded     (Refunded)
```

### **Payment Statuses**
```
- pending   (Not paid yet)
- paid      (Payment successful)
- failed    (Payment failed)
- refunded  (Money returned)
```

### **Payment Methods**
```
- credit_card
- debit_card
- paypal
- cash
- bank_transfer
```

---

## 🎯 Common Testing Workflows

### **Workflow 1: Customer Shopping**
1. Login as customer
2. Browse products (`GET /products`)
3. Add to cart (`POST /cart/items`)
4. View cart (`GET /cart`)
5. Validate cart (`GET /cart/validate`)
6. Create order (`POST /orders`)
7. View order (`GET /orders/{id}`)

### **Workflow 2: Staff Processing Order**
1. Login as cashier/manager
2. View today's orders (`GET /orders/today`)
3. Search specific order (`GET /orders/search?number=XXX`)
4. Confirm order (`PUT /orders/{id}/status` → "confirmed")
5. Update payment (`PUT /orders/{id}/payment-status` → "paid")
6. Mark as shipped (`POST /orders/{id}/ship`)

### **Workflow 3: Manager Product Management**
1. Login as manager
2. Create category (`POST /categories`)
3. Create product (`POST /products`)
4. Update product (`PUT /products/{id}`)
5. Update stock (`PUT /products/{id}/stock`)

### **Workflow 4: Admin User Management**
1. Login as admin
2. List all users (`GET /users`)
3. Change user role (`PUT /users/{id}/role`)
4. Ban user (`PUT /users/{id}/ban`)
5. Reset password (`POST /users/{id}/reset-password`)

---

## 🔄 Token Management

### **Access Token**
- Valid for: 1 hour (3600 seconds)
- Use in header: `Authorization: Bearer {access_token}`
- Auto-saved in Postman environment variable

### **Refresh Token**
- Valid for: 30 days (2592000 seconds)
- Use to get new access token when expired
- Endpoint: `POST /auth/refresh`

### **Example Token Refresh**
```bash
# When access token expires, use refresh token
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer {refresh_token}"
```

---

## 🧪 Sample Request Bodies

### **Register Customer**
```json
{
  "email": "test@example.com",
  "username": "testuser",
  "password": "Password123",
  "role": "customer",
  "first_name": "Test",
  "last_name": "User",
  "phone": "+1234567890",
  "address_line1": "123 Test St",
  "city": "Test City",
  "state": "TS",
  "postal_code": "12345",
  "country": "USA"
}
```

### **Login**
```json
{
  "email_or_username": "admin@ecommerce.com",
  "password": "Admin123!"
}
```

### **Create Product**
```json
{
  "name": "Test Product",
  "description": "A test product",
  "price": 99.99,
  "sku": "TEST-001",
  "barcode": "1234567890",
  "stock_quantity": 100,
  "category_id": 1,
  "is_active": true,
  "is_featured": false
}
```

### **Add to Cart**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

### **Create Order**
```json
{
  "shipping_address": {
    "line1": "123 Main St",
    "line2": "Apt 4B",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA"
  },
  "payment_method": "credit_card",
  "customer_notes": "Please deliver after 5 PM"
}
```

### **Update Order Status**
```json
{
  "status": "confirmed"
}
```

---

## 🚨 Common HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (not logged in or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

---

## 💡 Quick Tips

1. **Always check permissions** - Different endpoints require different roles
2. **Use environment variables** - Store `base_url` and tokens in Postman environment
3. **Token expires after 1 hour** - Use refresh endpoint to get new token
4. **Check enum values** - Use exact values from enum reference
5. **Start with seeded data** - Makes testing easier with pre-populated database

---

## 📱 Postman Collection Structure

```
1. Authentication (8 requests)
2. Categories (6 requests)
3. Products (7 requests)
4. Cart (6 requests)
5. Orders (13 requests)
6. User Management (11 requests)
7. Health Check (1 request)
```

**Total: 52 API endpoints** ready to test!

---

## ✅ Testing Checklist

- [ ] Health check works
- [ ] Can register new user
- [ ] Can login with all roles
- [ ] Token refresh works
- [ ] Public endpoints work without auth
- [ ] Protected endpoints require auth
- [ ] Role-based permissions work correctly
- [ ] Cart operations work
- [ ] Order creation works
- [ ] Order status updates work
- [ ] Product CRUD works
- [ ] Category CRUD works
- [ ] User management works (admin only)

---

**Happy Testing! 🚀**
