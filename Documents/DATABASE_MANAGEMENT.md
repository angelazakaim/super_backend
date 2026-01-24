# 🗄️ DATABASE MANAGEMENT GUIDE

## 📋 Table of Contents
1. [Understanding Migrations](#understanding-migrations)
2. [Using seed_data.py](#using-seed_datapy)
3. [Step-by-Step Instructions](#step-by-step-instructions)
4. [Common Scenarios](#common-scenarios)
5. [Troubleshooting](#troubleshooting)

---

## 🎯 Understanding Migrations

### **What is the migrations folder?**
```
migrations/
├── alembic.ini
├── env.py
├── script.py.mako
└── versions/
    ├── abc123_initial.py
    ├── def456_add_products.py
    └── ghi789_add_orders.py
```

**Purpose:** Track database schema changes over time
- Each file in `versions/` is a "migration" (a database change)
- Like Git commits, but for your database schema
- Allows you to upgrade/downgrade your database

### **When to use migrations vs seed_data.py?**

| Task | Use | Why |
|------|-----|-----|
| **Change database structure** | Migrations | Preserves existing data |
| **Add new table/column** | Migrations | Safe for production |
| **Populate test data** | seed_data.py | Fast, for development |
| **Reset everything** | seed_data.py | Clean slate |

---

## 🌱 Using seed_data.py

### **What does it do?**
```python
db.drop_all()    # ⚠️ DELETES ALL DATA!
db.create_all()  # Creates fresh tables
# Then populates with test data
```

**⚠️ WARNING:** This **destroys all existing data**!

### **What it creates:**
```
Users:
✅ admin@supermarket.com / admin123 (admin role)
✅ manager@test.com / manager123 (manager role) ⭐
✅ customer@test.com / customer123 (customer role)
✅ cashier@supermarket.com / cashier123 (cashier role)

Categories:
✅ 6 categories (Fruits, Beverages, Bakery, etc.)

Products:
✅ 11 sample products with images
✅ 6 featured products
✅ Some with discounts
```

---

## 📝 Step-by-Step Instructions

### **SCENARIO 1: First Time Setup (New Database)**

```bash
# 1. Make sure your backend is set up
cd your-backend-folder

# 2. Initialize migrations (ONLY ONCE EVER!)
flask db init

# 3. Create initial migration
flask db migrate -m "Initial setup"

# 4. Apply migration
flask db upgrade

# 5. Populate with test data
python seed_data.py
```

**Result:** Fresh database with migrations tracking + test data

---

### **SCENARIO 2: Reset Database (Development)**

**Use this when you want to start over with fresh test data.**

```bash
# Option A: Quick Reset (Recommended for Development)
python seed_data.py
```

**What happens:**
```
1. Drops all tables (deletes everything)
2. Creates fresh tables
3. Populates with test data
4. ⚠️ Migrations folder is NOT deleted
```

**Result:** Clean database with test data

```bash
# Option B: Complete Reset (Nuclear Option)
rm -rf migrations/        # Delete migrations folder
rm instance/*.db          # Delete database file (SQLite)
flask db init             # Recreate migrations
flask db migrate -m "Initial setup"
flask db upgrade
python seed_data.py
```

**Result:** Everything reset from scratch

---

### **SCENARIO 3: You Changed Your Models**

**Example:** You added a new field to Product model

```python
# models/product.py
class Product(db.Model):
    # ... existing fields ...
    brand = db.Column(db.String(100))  # NEW FIELD
```

**Steps:**
```bash
# 1. Create migration for the change
flask db migrate -m "Add brand field to products"

# 2. Review the migration file (optional)
cat migrations/versions/latest_file.py

# 3. Apply the migration
flask db upgrade

# 4. (Optional) Reset test data
python seed_data.py
```

**Result:** Database updated, existing data preserved (if not using seed_data.py)

---

### **SCENARIO 4: Production Deployment**

**⚠️ NEVER use seed_data.py in production!**

```bash
# Production workflow:

# 1. Apply migrations only
flask db upgrade

# 2. Do NOT run seed_data.py
# (Production data is real customer data!)
```

---

## 🔧 Common Scenarios

### **"I want to test my frontend with fresh data"**
```bash
python seed_data.py
```
✅ Fast, simple, gives you test users immediately

---

### **"I added a new table/column to my models"**
```bash
flask db migrate -m "Description of change"
flask db upgrade
```
✅ Preserves existing data

---

### **"My database is corrupted/messed up"**
```bash
# Development only!
python seed_data.py
```
✅ Clean slate

---

### **"I want to keep migrations in sync"**
```bash
# If you used seed_data.py but want migrations too:
flask db stamp head
```
✅ Tells Flask-Migrate that database matches current code

---

## 🗂️ What to Do with Migrations Folder?

### **Development (Your Local Machine)**

**Option 1: Keep It** ✅ Recommended
```bash
# Keep migrations folder
# Just run seed_data.py when you need fresh data
python seed_data.py

# Migrations stay in sync
flask db stamp head  # Optional: mark current state
```

**Option 2: Delete It** (If you always use seed_data.py)
```bash
rm -rf migrations/
# Just use seed_data.py for everything
python seed_data.py
```

### **Production**

**Always Keep It!** ✅ Required
```bash
# Never delete migrations in production
# Never run seed_data.py in production

# Only run:
flask db upgrade
```

---

## 🎯 Quick Reference

| Command | What It Does | Safe for Production? |
|---------|-------------|---------------------|
| `flask db init` | Create migrations folder | Only once |
| `flask db migrate -m "msg"` | Create new migration | Yes ✅ |
| `flask db upgrade` | Apply migrations | Yes ✅ |
| `flask db downgrade` | Revert migrations | Careful ⚠️ |
| `python seed_data.py` | Reset DB with test data | NO ❌ |
| `flask db stamp head` | Mark current state | Yes ✅ |

---

## 🐛 Troubleshooting

### **Error: "Target database is not up to date"**
```bash
# Solution:
flask db stamp head
flask db upgrade
```

### **Error: "Can't locate revision"**
```bash
# Solution: Delete and recreate migrations
rm -rf migrations/
flask db init
flask db migrate -m "Initial setup"
flask db upgrade
```

### **Error: "No such table"**
```bash
# Solution:
python seed_data.py
# OR
flask db upgrade
```

### **Error: "UNIQUE constraint failed"**
```bash
# Solution: Database already has data
python seed_data.py  # Resets everything
```

---

## 📚 Recommended Workflow

### **For Development (Your Machine)**

```bash
# Daily work:
1. Edit your models
2. Run: flask db migrate -m "description"
3. Run: flask db upgrade
4. When you need fresh test data: python seed_data.py

# Starting fresh:
1. Run: python seed_data.py
2. Test your app with sample data
```

### **For Production**

```bash
# Deployment:
1. Pull latest code
2. Run: flask db upgrade
3. NEVER run seed_data.py
```

---

## 🎓 Key Concepts

### **seed_data.py is for DEVELOPMENT**
- ✅ Fast way to get test data
- ✅ Perfect for frontend testing
- ❌ Destroys all data
- ❌ Never use in production

### **Migrations are for PRODUCTION**
- ✅ Safe database schema changes
- ✅ Preserves existing data
- ✅ Can upgrade/downgrade
- ✅ Essential for teams

### **Both can coexist!**
```bash
# Development workflow:
1. Use migrations to track schema changes
2. Use seed_data.py to reset test data
3. Run flask db stamp head to keep them in sync
```

---

## ✅ Your Current Situation

Based on your files, here's what to do:

### **Step 1: Copy seed_data.py to your backend**
```bash
# Copy the new seed_data.py to your Flask backend root
cp seed_data.py /path/to/your/backend/
```

### **Step 2: Run it**
```bash
cd /path/to/your/backend/
python seed_data.py
```

### **Step 3: Test your frontend**
```bash
# Start backend
flask run

# Start frontend  
npm run dev

# Login with:
# Manager: manager@test.com / manager123
# Customer: customer@test.com / customer123
```

---

## 🎯 Summary

**TL;DR:**

```bash
# Fresh start (development):
python seed_data.py

# Changed models:
flask db migrate -m "what changed"
flask db upgrade

# Production:
flask db upgrade  # NEVER seed_data.py!
```

**Remember:**
- seed_data.py = Fresh test data (deletes everything)
- Migrations = Schema changes (keeps data)
- Both work together in development!

---

**Ready to test! Your frontend will now have proper login credentials! 🚀**
