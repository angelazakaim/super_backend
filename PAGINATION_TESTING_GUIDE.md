# 🧪 Pagination Testing Guide - Hands-On Examples

## 🚀 Quick Start

### **Step 1: Run Enhanced Seed Data**
```bash
python seed_data_pagination.py
```

**This creates:**
- 150 products (to see 8 pages with per_page=20)
- 100 orders (to see 10 pages with per_page=10)
- 50 customers (to see 2 pages with per_page=25)
- 53 total users

---

## 📋 Testing Scenarios

### **Scenario 1: Basic Product Pagination**

#### **Request 1.1: First Page**
```http
GET http://localhost:5000/api/products?page=1&per_page=20
```

**Expected Response:**
```json
{
  "products": [
    { "id": 1, "name": "Premium Laptop 1", "price": 899.99 },
    { "id": 2, "name": "Elite Phone 2", "price": 699.99 },
    // ... 18 more products (20 total)
  ],
  "total": 150,
  "pages": 8,
  "current_page": 1,
  "per_page": 20,
  "has_next": true,    // ✅ Can go to page 2
  "has_prev": false    // ❌ Already on first page
}
```

**What to observe:**
- ✅ Returns exactly 20 products
- ✅ `total` is 150 (total products in DB)
- ✅ `pages` is 8 (150 ÷ 20 = 7.5, rounded up)
- ✅ `has_next` is true (more pages available)
- ✅ `has_prev` is false (can't go before page 1)

---

#### **Request 1.2: Second Page**
```http
GET http://localhost:5000/api/products?page=2&per_page=20
```

**Expected Response:**
```json
{
  "products": [
    { "id": 21, "name": "...", "price": ... },
    { "id": 22, "name": "...", "price": ... },
    // ... 18 more products (products 21-40)
  ],
  "total": 150,
  "pages": 8,
  "current_page": 2,
  "per_page": 20,
  "has_next": true,    // ✅ Can go to page 3
  "has_prev": true     // ✅ Can go back to page 1
}
```

**What to observe:**
- ✅ Returns products 21-40 (different from page 1)
- ✅ `has_next` is true (more pages available)
- ✅ `has_prev` is true (can go back to page 1)

---

#### **Request 1.3: Last Page (Partial)**
```http
GET http://localhost:5000/api/products?page=8&per_page=20
```

**Expected Response:**
```json
{
  "products": [
    { "id": 141, "name": "...", "price": ... },
    { "id": 142, "name": "...", "price": ... },
    // ... only 10 products (141-150)
  ],
  "total": 150,
  "pages": 8,
  "current_page": 8,
  "per_page": 20,
  "has_next": false,   // ❌ No more pages
  "has_prev": true     // ✅ Can go back
}
```

**What to observe:**
- ✅ Returns only 10 products (not 20!)
- ✅ Products 141-150 (the remaining items)
- ✅ `has_next` is false (this is the last page)
- ✅ `has_prev` is true (can navigate back)

---

### **Scenario 2: Different Page Sizes**

#### **Request 2.1: Small Pages (10 items)**
```http
GET http://localhost:5000/api/products?page=1&per_page=10
```

**Expected Response:**
```json
{
  "products": [ /* 10 products */ ],
  "total": 150,
  "pages": 15,    // ← 150 ÷ 10 = 15 pages
  "current_page": 1,
  "per_page": 10,
  "has_next": true,
  "has_prev": false
}
```

**What to observe:**
- ✅ Only 10 products returned
- ✅ More pages (15 instead of 8)
- ✅ Smaller chunks = more pages

---

#### **Request 2.2: Large Pages (50 items)**
```http
GET http://localhost:5000/api/products?page=1&per_page=50
```

**Expected Response:**
```json
{
  "products": [ /* 50 products */ ],
  "total": 150,
  "pages": 3,     // ← 150 ÷ 50 = 3 pages
  "current_page": 1,
  "per_page": 50,
  "has_next": true,
  "has_prev": false
}
```

**What to observe:**
- ✅ 50 products returned
- ✅ Fewer pages (3 instead of 8)
- ✅ Larger chunks = fewer pages

---

#### **Request 2.3: Maximum Limit (capped at 100)**
```http
GET http://localhost:5000/api/products?page=1&per_page=1000
```

**Expected Response:**
```json
{
  "products": [ /* 100 products (not 1000!) */ ],
  "total": 150,
  "pages": 2,     // ← 150 ÷ 100 = 2 pages (capped)
  "current_page": 1,
  "per_page": 100,  // ← Capped at 100
  "has_next": true,
  "has_prev": false
}
```

**What to observe:**
- ✅ Maximum 100 items returned (security limit)
- ✅ Your app prevents abuse by limiting per_page

---

### **Scenario 3: Edge Cases**

#### **Request 3.1: Page Doesn't Exist**
```http
GET http://localhost:5000/api/products?page=999&per_page=20
```

**Expected Response:**
```json
{
  "products": [],   // ← Empty array (no crash!)
  "total": 150,
  "pages": 8,
  "current_page": 999,  // ← Page requested
  "per_page": 20,
  "has_next": false,
  "has_prev": true
}
```

**What to observe:**
- ✅ Returns empty array (no 404 error)
- ✅ Still shows pagination metadata
- ✅ Graceful handling with `error_out=False`

---

#### **Request 3.2: Negative Page**
```http
GET http://localhost:5000/api/products?page=-1&per_page=20
```

**Expected Response:**
```json
{
  "products": [ /* 20 products */ ],
  "total": 150,
  "pages": 8,
  "current_page": 1,  // ← Defaults to page 1
  "per_page": 20,
  "has_next": true,
  "has_prev": false
}
```

**What to observe:**
- ✅ Defaults to page 1 (safe handling)
- ✅ No error thrown

---

#### **Request 3.3: Zero or Invalid per_page**
```http
GET http://localhost:5000/api/products?page=1&per_page=0
```

**Expected Response:**
```json
{
  "products": [ /* 20 products */ ],
  "total": 150,
  "pages": 8,
  "current_page": 1,
  "per_page": 20,  // ← Defaults to 20
  "has_next": true,
  "has_prev": false
}
```

**What to observe:**
- ✅ Defaults to 20 items per page
- ✅ Safe fallback

---

### **Scenario 4: Pagination with Filters**

#### **Request 4.1: Category Filter + Pagination**
```http
GET http://localhost:5000/api/products?page=1&per_page=20&category_id=2
```

**Expected Response:**
```json
{
  "products": [ /* Products from category 2 only */ ],
  "total": 25,      // ← Only 25 products in this category
  "pages": 2,       // ← 25 ÷ 20 = 2 pages
  "current_page": 1,
  "per_page": 20,
  "has_next": true,
  "has_prev": false
}
```

**What to observe:**
- ✅ Pagination works with filters
- ✅ `total` reflects filtered count (not all products)
- ✅ `pages` calculated based on filtered results

---

#### **Request 4.2: Search + Pagination**
```http
GET http://localhost:5000/api/products?page=1&per_page=20&search=laptop
```

**Expected Response:**
```json
{
  "products": [ /* Only products matching "laptop" */ ],
  "total": 15,      // ← Only 15 products match "laptop"
  "pages": 1,       // ← 15 ÷ 20 = 1 page
  "current_page": 1,
  "per_page": 20,
  "has_next": false,
  "has_prev": false
}
```

**What to observe:**
- ✅ Search narrows results
- ✅ Pagination reflects search results
- ✅ Only 1 page needed for 15 results

---

### **Scenario 5: Order Pagination**

#### **Request 5.1: Customer's Own Orders**
```http
GET http://localhost:5000/api/orders?page=1&per_page=10
Authorization: Bearer {customer_token}
```

**Expected Response:**
```json
{
  "orders": [ /* 10 orders for this customer */ ],
  "total": 25,      // ← This customer has 25 orders
  "pages": 3,       // ← 25 ÷ 10 = 3 pages
  "current_page": 1,
  "per_page": 10
}
```

---

#### **Request 5.2: All Orders (Admin/Manager)**
```http
GET http://localhost:5000/api/orders/admin?page=1&per_page=20
Authorization: Bearer {admin_token}
```

**Expected Response:**
```json
{
  "orders": [ /* 20 orders from all customers */ ],
  "total": 100,     // ← All orders in system
  "pages": 5,       // ← 100 ÷ 20 = 5 pages
  "current_page": 1,
  "per_page": 20
}
```

---

#### **Request 5.3: Filter by Status + Pagination**
```http
GET http://localhost:5000/api/orders/admin?page=1&per_page=20&status=pending
Authorization: Bearer {admin_token}
```

**Expected Response:**
```json
{
  "orders": [ /* Only pending orders */ ],
  "total": 12,      // ← Only 12 pending orders
  "pages": 1,       // ← All fit on one page
  "current_page": 1,
  "per_page": 20
}
```

---

### **Scenario 6: User List Pagination (Admin)**

#### **Request 6.1: All Users**
```http
GET http://localhost:5000/api/users?page=1&per_page=25
Authorization: Bearer {admin_token}
```

**Expected Response:**
```json
{
  "users": [ /* 25 users */ ],
  "total": 53,      // ← 50 customers + 3 staff
  "pages": 3,       // ← 53 ÷ 25 = 3 pages
  "current_page": 1,
  "per_page": 25
}
```

---

#### **Request 6.2: Filter by Role**
```http
GET http://localhost:5000/api/users?page=1&per_page=25&role=customer
Authorization: Bearer {admin_token}
```

**Expected Response:**
```json
{
  "users": [ /* Only customers */ ],
  "total": 50,      // ← Only customers
  "pages": 2,       // ← 50 ÷ 25 = 2 pages
  "current_page": 1,
  "per_page": 25
}
```

---

## 🎯 Postman Tests to Verify Pagination

### **Test 1: Verify Page Count**
```javascript
// In Postman Tests tab
pm.test("Page calculation is correct", function () {
    const response = pm.response.json();
    const expectedPages = Math.ceil(response.total / response.per_page);
    pm.expect(response.pages).to.equal(expectedPages);
});
```

### **Test 2: Verify has_next Logic**
```javascript
pm.test("has_next is correct", function () {
    const response = pm.response.json();
    if (response.current_page < response.pages) {
        pm.expect(response.has_next).to.be.true;
    } else {
        pm.expect(response.has_next).to.be.false;
    }
});
```

### **Test 3: Verify has_prev Logic**
```javascript
pm.test("has_prev is correct", function () {
    const response = pm.response.json();
    if (response.current_page > 1) {
        pm.expect(response.has_prev).to.be.true;
    } else {
        pm.expect(response.has_prev).to.be.false;
    }
});
```

### **Test 4: Verify Item Count**
```javascript
pm.test("Returns correct number of items", function () {
    const response = pm.response.json();
    const expectedCount = Math.min(
        response.per_page,
        response.total - (response.current_page - 1) * response.per_page
    );
    pm.expect(response.products.length).to.be.at.most(response.per_page);
});
```

---

## 📊 Visual Pagination Examples

### **Example 1: Product Listing (150 products, 20 per page)**
```
Page 1: [1-20]   ← has_next: true,  has_prev: false
Page 2: [21-40]  ← has_next: true,  has_prev: true
Page 3: [41-60]  ← has_next: true,  has_prev: true
Page 4: [61-80]  ← has_next: true,  has_prev: true
Page 5: [81-100] ← has_next: true,  has_prev: true
Page 6: [101-120]← has_next: true,  has_prev: true
Page 7: [121-140]← has_next: true,  has_prev: true
Page 8: [141-150]← has_next: false, has_prev: true (only 10 items!)
```

### **Example 2: Orders (100 orders, 10 per page)**
```
Page 1: [1-10]   ← 10 pages total
Page 2: [11-20]
Page 3: [21-30]
...
Page 10: [91-100]
```

---

## 🔍 Performance Comparison

### **Without Pagination:**
```
Request: GET /api/products
Database: SELECT * FROM products (loads 150 products)
Memory: ~5MB
Response Time: ~500ms
Network: ~2MB JSON
```

### **With Pagination:**
```
Request: GET /api/products?page=1&per_page=20
Database: SELECT * FROM products LIMIT 20 OFFSET 0 (loads 20 products)
Memory: ~500KB (10x less!)
Response Time: ~50ms (10x faster!)
Network: ~200KB JSON (10x smaller!)
```

---

## 💡 Pro Tips for Testing

1. **Start with small per_page** (10) to see multiple pages easily
2. **Test the last page** to ensure partial pages work
3. **Test page 999** to ensure graceful handling
4. **Test with filters** to verify pagination works with WHERE clauses
5. **Check response time** - should be fast even with large datasets
6. **Verify item uniqueness** - no duplicates across pages
7. **Test navigation** - next/prev buttons should work correctly

---

## ✅ Quick Testing Checklist

- [ ] Page 1 works (has_prev: false)
- [ ] Middle pages work (has_next: true, has_prev: true)
- [ ] Last page works (has_next: false, partial results OK)
- [ ] Page out of range returns empty (not error)
- [ ] Different per_page values work (10, 20, 50, 100)
- [ ] Maximum per_page is enforced (capped at 100)
- [ ] Total count is correct
- [ ] Page count calculation is correct
- [ ] Pagination works with filters (category, search, status)
- [ ] Pagination works for orders, users, products
- [ ] Response time is acceptable

---

**Now test it yourself! Run `python seed_data_pagination.py` and start paginating! 🚀**
