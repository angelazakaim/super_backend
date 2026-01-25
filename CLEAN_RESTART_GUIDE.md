# 🔄 Clean Database Restart Guide

This guide will help you completely reset your database and start fresh with new migrations.

---

## 📋 Prerequisites

Make sure you have:
- Python virtual environment activated
- All dependencies installed (`pip install -r requirements.txt`)
- Flask app configured properly

---

## 🗑️ Step 1: Stop Your Flask Application

**Important:** Stop any running Flask servers before proceeding!

```bash
# Press Ctrl+C in the terminal where Flask is running
# Or close the terminal window
```

---

## 🧹 Step 2: Delete Instance and Migrations Folders

### **Option A: Using Command Line (Recommended)**

#### **Windows (PowerShell):**
```powershell
# Navigate to your project root
cd path\to\your\project

# Delete instance folder
Remove-Item -Recurse -Force instance

# Delete migrations folder
Remove-Item -Recurse -Force migrations

# Verify deletion
ls
```

#### **Windows (Command Prompt):**
```cmd
# Navigate to your project root
cd path\to\your\project

# Delete instance folder
rmdir /s /q instance

# Delete migrations folder
rmdir /s /q migrations

# Verify deletion
dir
```

#### **Linux/Mac:**
```bash
# Navigate to your project root
cd path/to/your/project

# Delete instance and migrations folders
rm -rf instance migrations

# Verify deletion
ls -la
```

### **Option B: Using File Explorer / Finder**

1. Open your project folder in File Explorer (Windows) or Finder (Mac)
2. Find the `instance` folder → **Delete it**
3. Find the `migrations` folder → **Delete it**
4. Empty the Recycle Bin/Trash (optional but recommended)

---

## 🏗️ Step 3: Initialize Fresh Database

### **3.1 Create New Migrations Folder**

```bash
# Make sure you're in your project root and virtual environment is activated
flask db init
```

**Expected Output:**
```
Creating directory migrations ... done
Creating directory migrations/versions ... done
Generating migrations/alembic.ini ... done
...
```

### **3.2 Create Initial Migration**

```bash
flask db migrate -m "Initial migration with all models"
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'user'
INFO  [alembic.autogenerate.compare] Detected added table 'category'
INFO  [alembic.autogenerate.compare] Detected added table 'customer'
INFO  [alembic.autogenerate.compare] Detected added table 'employee'
INFO  [alembic.autogenerate.compare] Detected added table 'product'
INFO  [alembic.autogenerate.compare] Detected added table 'cart'
INFO  [alembic.autogenerate.compare] Detected added table 'order'
INFO  [alembic.autogenerate.compare] Detected added table 'cart_item'
INFO  [alembic.autogenerate.compare] Detected added table 'order_item'
  Generating migrations/versions/xxxxxxxxxxxx_initial_migration_with_all_models.py ... done
```

### **3.3 Apply Migration to Create Tables**

```bash
flask db upgrade
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> xxxxx, Initial migration with all models
```

---

## 🌱 Step 4: Seed the Database with Test Data

### **4.1 Run the Seed Script**

```bash
python seed_data.py
```

**Expected Output:**
```
============================================================
🌱 SEEDING DATABASE
============================================================
🗑️  Clearing existing data...
✅ All data cleared!

👥 Creating users...
  ✓ Created admin user
  ✓ Created manager user
  ✓ Created cashier user
  ✓ Created 5 customer users
✅ Total users created: 8

👔 Creating employee profiles...
✅ Created 2 employee profiles

🛍️  Creating customer profiles...
✅ Created 5 customer profiles

📂 Creating categories...
✅ Created 12 categories (5 root, 7 subcategories)

📦 Creating products...
✅ Created 17 products

🛒 Creating shopping carts...
✅ Created 3 carts with 9 items total

📋 Creating orders...
✅ Created 12 orders with 28 order items
   - Pending: 1
   - Confirmed: 2
   - Processing: 1
   - Shipped: 2
   - Delivered: 5
   - Cancelled: 1

============================================================
✅ DATABASE SEEDING COMPLETE!
============================================================

📊 Summary:
   Users: 8
   Customers: 5
   Employees: 2
   Categories: 12
   Products: 17
   Carts: 3
   Cart Items: 9
   Orders: 12
   Order Items: 28

🔑 Test Accounts:
   Admin:
     Email: admin@ecommerce.com
     Password: Admin123!

   Manager:
     Email: manager@ecommerce.com
     Password: Manager123!

   Cashier:
     Email: cashier@ecommerce.com
     Password: Cashier123!

   Customer (example):
     Email: john.doe@email.com
     Password: Customer123!
============================================================
```

---

## 🚀 Step 5: Start Your Application

```bash
python run.py
# or
flask run
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

## ✅ Step 6: Verify Everything Works

### **6.1 Test Health Endpoint**

```bash
curl http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy"
}
```

### **6.2 Test Login with Seed Data**

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_username": "admin@ecommerce.com",
    "password": "Admin123!"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": 1,
    "email": "admin@ecommerce.com",
    "username": "admin",
    "role": "admin",
    "is_active": true
  }
}
```

---

## 🧪 Step 7: Import Postman Collection

1. Open Postman
2. Click **Import** button (top left)
3. Select the file: `Ecommerce_API_Complete.postman_collection.json`
4. Click **Import**
5. Create a new **Environment** in Postman:
   - Variable: `base_url` → Value: `http://localhost:5000/api`
   - Variable: `access_token` → Value: (leave empty, will auto-fill)
   - Variable: `refresh_token` → Value: (leave empty, will auto-fill)

6. Start testing! 🎉

---

## 📝 Complete Command Summary

Here's the complete sequence for copy-paste:

### **Windows (PowerShell):**
```powershell
# Stop Flask server (Ctrl+C)

# Delete old files
Remove-Item -Recurse -Force instance
Remove-Item -Recurse -Force migrations

# Create new database
flask db init
flask db migrate -m "Initial migration with all models"
flask db upgrade

# Seed data
python seed_data.py

# Start server
python run.py
```

### **Linux/Mac:**
```bash
# Stop Flask server (Ctrl+C)

# Delete old files
rm -rf instance migrations

# Create new database
flask db init
flask db migrate -m "Initial migration with all models"
flask db upgrade

# Seed data
python seed_data.py

# Start server
python run.py
```

---

## 🔍 Troubleshooting

### **Problem: "flask: command not found"**

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Verify Flask is installed
pip list | grep Flask
```

### **Problem: "No such file or directory: 'instance'"**

**Solution:** This is normal if the folder doesn't exist. Just skip the deletion and proceed to Step 3.

### **Problem: Migration fails with "Table already exists"**

**Solution:**
```bash
# Delete the database file manually
rm instance/ecommerce_dev.db  # Linux/Mac
del instance\ecommerce_dev.db  # Windows

# Then run migrations again
flask db upgrade
```

### **Problem: Seed script fails**

**Solution:**
```bash
# Make sure you've run migrations first
flask db upgrade

# Then run seed script
python seed_data.py
```

### **Problem: "Permission denied" when deleting folders**

**Solution:**
- **Windows:** Run PowerShell as Administrator
- **Mac/Linux:** Use `sudo rm -rf instance migrations` (be careful!)
- Or delete manually using File Explorer/Finder

---

## 📊 What Gets Created

### **Users (8 total):**
- 1 Admin (admin@ecommerce.com)
- 1 Manager (manager@ecommerce.com)
- 1 Cashier (cashier@ecommerce.com)
- 5 Customers (john.doe@email.com, jane.smith@email.com, etc.)

### **Categories (12 total):**
- 5 Root categories (Electronics, Clothing, Home & Garden, Sports, Books)
- 7 Subcategories (Computers, Smartphones, Audio, Men's Clothing, Women's Clothing, Furniture, Kitchen)

### **Products (17 total):**
- Electronics: Laptops, phones, headphones, mice, keyboards
- Clothing: Jeans, t-shirts, dresses, yoga pants
- Home: Office chairs, desks, mixers, blenders
- Mix of featured and regular products
- Varying stock levels (some low stock items)

### **Orders (12 total):**
- Different statuses: pending, confirmed, processing, shipped, delivered, cancelled
- Different payment statuses: pending, paid, failed, refunded
- Assigned to different customers
- Contains 1-4 products each

### **Shopping Carts (3 total):**
- First 3 customers have carts with 2-4 items each
- Ready for testing cart operations

---

## 🎯 Next Steps

After completing the clean restart:

1. ✅ Test all endpoints using Postman collection
2. ✅ Verify role-based access control (admin, manager, cashier, customer)
3. ✅ Test cart and order workflows
4. ✅ Verify enum validation is working
5. ✅ Check product stock management
6. ✅ Test payment status updates

---

## 🆘 Need Help?

If you encounter any issues:

1. Check the Flask application logs in the terminal
2. Verify your `.env` file is configured correctly
3. Ensure all dependencies are installed: `pip install -r requirements.txt`
4. Make sure you're in the project root directory
5. Confirm virtual environment is activated

---

## ✨ You're Done!

Your database is now clean, freshly migrated, and seeded with comprehensive test data. You can start testing all CRUD operations using the Postman collection!

**Happy Testing! 🚀**
