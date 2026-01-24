# 🧪 Complete API Testing Guide

## 📦 Postman Collection: 68 Requests Testing All CRUD Operations

### Quick Start
1. **Import:** `E-Commerce_4Role_API_Complete.postman_collection.json`
2. **Set base_url:** `http://localhost:5000` (already set)
3. **Run:** Authentication folder first, then others in order

---

## 📋 Collection Structure (68 Requests)

### 1. Authentication (10 requests)
- Register Customer, Cashier, Manager, Admin
- Login all roles (auto-saves tokens)
- Test password change

### 2. Categories (7 requests)
- Admin creates category ✅
- Manager creates category ❌ (403)
- Manager creates subcategory ✅
- Public views categories ✅

### 3. Products (14 requests)
- Manager creates product ✅
- Cashier creates product ❌ (403)
- Manager updates stock ✅
- Manager changes price ❌ (403)
- Admin changes price ✅

### 4. Cart (6 requests)
- Customer manages cart
- Add, update, remove, clear
- Validate before checkout

### 5. Orders (14 requests)
- Customer creates order ✅
- Cashier updates status ✅
- Cashier marks delivered ❌ (403)
- Manager views 30-day orders ✅
- Admin views all orders ✅
- Admin processes refund ✅

### 6. User Management (13 requests)
- View/update own profile ✅
- Admin creates users ✅
- Admin changes roles ✅
- Admin bans users ✅
- Admin resets passwords ✅

### 7. Permission Tests (4 requests)
- All should return 403 Forbidden
- Verifies RBAC works correctly

---

## 🎯 Auto-Saved Variables

Tokens automatically saved on login:
- `{{customer_token}}`
- `{{cashier_token}}`
- `{{manager_token}}`
- `{{admin_token}}`

IDs automatically saved on creation:
- `{{product_id}}`
- `{{category_id}}`
- `{{order_id}}`
- `{{test_user_id}}`

---

## ✅ Testing Workflow

**Run in order:**
1. Authentication → Saves all tokens
2. Categories → Saves category_id
3. Products → Saves product_id
4. Cart → Tests shopping cart
5. Orders → Saves order_id
6. User Management → Tests admin operations
7. Permission Tests → Verifies role restrictions

**Expected Results:**
- ✅ 64 successful requests (200/201)
- ❌ 4 forbidden requests (403) in Permission Tests

---

## 🔍 What's Tested

### CRUD Operations ✅
- All entities: Categories, Products, Orders, Users
- All operations: Create, Read, Update, Delete

### Role Permissions ✅
- Customer: Cart, own orders
- Cashier: POS operations, order processing
- Manager: Inventory, order management
- Admin: Prices, refunds, user management

### Permission Restrictions ✅
- Manager cannot change prices
- Cashier cannot create products
- Customer cannot view all orders
- Manager cannot delete categories

### Business Logic ✅
- Stock validation
- Order workflows
- Cart validation
- Atomic transactions

---

## 🚀 Ready to Test!

Import collection → Start server → Run Authentication → Test complete! 🎉
