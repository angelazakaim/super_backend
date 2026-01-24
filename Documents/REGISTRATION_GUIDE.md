# 📝 User Registration Examples

## ✅ Correct Registration Formats

### 1. Simple Registration (Minimal)
```json
{
  "email": "john.doe@example.com",
  "username": "johndoe",
  "password": "John123!",
  "role": "customer"
}
```

---

### 2. Complete Customer Registration (Full Address)
```json
{
  "email": "jane.smith@example.com",
  "username": "janesmith",
  "password": "Jane123!",
  "role": "customer",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "(555) 123-4567",
  "address_line1": "123 Main Street",
  "address_line2": "Apt 4B",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "USA"
}
```

---

### 3. Customer with Partial Address
```json
{
  "email": "bob.wilson@example.com",
  "username": "bobwilson",
  "password": "Bob123!",
  "role": "customer",
  "first_name": "Bob",
  "last_name": "Wilson",
  "phone": "(555) 987-6543",
  "address_line1": "456 Oak Avenue",
  "city": "Boston",
  "state": "MA",
  "postal_code": "02101",
  "country": "USA"
}
```

---

### 4. Manager Registration
```json
{
  "email": "manager@example.com",
  "username": "manager1",
  "password": "Manager123!",
  "role": "manager",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "phone": "(555) 111-2222",
  "hire_date": "2024-01-15",
  "salary": 75000.00
}
```

---

### 5. Cashier Registration
```json
{
  "email": "cashier@example.com",
  "username": "cashier1",
  "password": "Cashier123!",
  "role": "cashier",
  "first_name": "Mike",
  "last_name": "Brown",
  "phone": "(555) 333-4444",
  "hire_date": "2024-03-01",
  "salary": 45000.00
}
```

---

## 📋 Field Descriptions

### Required Fields (All Users)
| Field | Type | Description |
|-------|------|-------------|
| `email` | string | Unique email address |
| `username` | string | Unique username |
| `password` | string | Min 8 chars, upper, lower, number, special |
| `role` | string | "customer", "manager", "cashier", or "admin" |

### Optional Customer Fields
| Field | Type | Description |
|-------|------|-------------|
| `first_name` | string | First name |
| `last_name` | string | Last name |
| `phone` | string | Phone number |
| `address_line1` | string | Street address line 1 |
| `address_line2` | string | Street address line 2 (apt, suite) |
| `city` | string | City |
| `state` | string | State/Province |
| `postal_code` | string | ZIP/Postal code |
| `country` | string | Country |

### Optional Employee Fields (Manager/Cashier)
| Field | Type | Description |
|-------|------|-------------|
| `first_name` | string | First name |
| `last_name` | string | Last name |
| `phone` | string | Phone number |
| `hire_date` | string | Hire date (YYYY-MM-DD) |
| `salary` | float | Annual salary |

---

## ❌ Common Mistakes

### Wrong - Using `address` field:
```json
{
  "email": "test@example.com",
  "username": "test",
  "password": "Test123!",
  "address": "123 Main St"  // ❌ WRONG! No "address" field
}
```

### Correct - Using address fields:
```json
{
  "email": "test@example.com",
  "username": "test",
  "password": "Test123!",
  "address_line1": "123 Main St",  // ✅ CORRECT!
  "city": "New York",
  "state": "NY",
  "postal_code": "10001"
}
```

---

## 🧪 Testing Sequence

### 1. Register Simple Customer
```json
POST {{base_url}}/api/auth/register

{
  "email": "customer1@example.com",
  "username": "customer1",
  "password": "Customer123!",
  "role": "customer"
}
```

Expected: **201 Created**

---

### 2. Register Customer with Full Address
```json
POST {{base_url}}/api/auth/register

{
  "email": "customer2@example.com",
  "username": "customer2",
  "password": "Customer123!",
  "role": "customer",
  "first_name": "Alice",
  "last_name": "Cooper",
  "phone": "(555) 555-5555",
  "address_line1": "789 Elm Street",
  "city": "Chicago",
  "state": "IL",
  "postal_code": "60601",
  "country": "USA"
}
```

Expected: **201 Created** with profile data

---

### 3. Try Duplicate Email
```json
POST {{base_url}}/api/auth/register

{
  "email": "customer1@example.com",  // Already exists!
  "username": "newuser",
  "password": "Test123!",
  "role": "customer"
}
```

Expected: **400 Bad Request** - "Email already registered"

---

### 4. Try Duplicate Username
```json
POST {{base_url}}/api/auth/register

{
  "email": "newemail@example.com",
  "username": "customer1",  // Already exists!
  "password": "Test123!",
  "role": "customer"
}
```

Expected: **400 Bad Request** - "Username already taken"

---

## 💡 Password Requirements

Valid passwords must have:
- ✅ At least 8 characters
- ✅ At least one uppercase letter
- ✅ At least one lowercase letter
- ✅ At least one number
- ✅ At least one special character

Examples of valid passwords:
- `Password123!`
- `MyPass@2024`
- `Secure#Pass1`
- `Test123$`

Examples of invalid passwords:
- `password` (no uppercase, number, special)
- `PASSWORD123` (no lowercase, special)
- `Pass123` (no special character, too short)
- `Pass!` (too short, no number)

---

## 📊 Expected Responses

### Success (201 Created)
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 5,
    "email": "test@example.com",
    "username": "testuser",
    "role": "customer",
    "is_active": true,
    "created_at": "2026-01-23T13:39:33.339631",
    "updated_at": "2026-01-23T13:39:33.339641"
  },
  "profile": {
    "id": 3,
    "user_id": 5,
    "first_name": "Test",
    "last_name": "User",
    "full_name": "Test User",
    "phone": "(555) 123-4567",
    "address": {
      "line1": "123 Main St",
      "line2": "Apt 4B",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "USA"
    },
    "created_at": "2026-01-23T13:39:33.400000",
    "updated_at": "2026-01-23T13:39:33.400000"
  }
}
```

### Error - Email Exists (400 Bad Request)
```json
{
  "error": "Email already registered"
}
```

### Error - Username Exists (400 Bad Request)
```json
{
  "error": "Username already taken"
}
```

### Error - Missing Field (400 Bad Request)
```json
{
  "error": "email is required"
}
```

---

## 🎯 Quick Test

Try this simple registration right now:

```json
POST {{base_url}}/api/auth/register

{
  "email": "quicktest@example.com",
  "username": "quicktest",
  "password": "Quick123!",
  "role": "customer",
  "first_name": "Quick",
  "last_name": "Test"
}
```

Should work perfectly! ✅
