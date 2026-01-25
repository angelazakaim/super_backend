"""
Quick Database Reset - Use this if you can lose test data.

This will:
1. Drop all tables
2. Create all tables with new schema
3. Ready for seed data

WARNING: This deletes ALL data!
"""


def reset_database():
    """Reset database with new schema."""
    from app import create_app
    from app.extensions import db
    
    app = create_app()
    
    with app.app_context():
        print("\n" + "⚠️  "*20)
        print("DATABASE RESET - THIS WILL DELETE ALL DATA!")
        print("⚠️  "*20 + "\n")
        
        response = input("Are you sure you want to continue? Type 'YES' to confirm: ")
        
        if response != 'YES':
            print("❌ Reset cancelled")
            return
        
        print("\n" + "="*60)
        print("Step 1: Dropping all tables...")
        print("="*60)
        db.drop_all()
        print("✅ All tables dropped")
        
        print("\n" + "="*60)
        print("Step 2: Creating all tables with new schema...")
        print("="*60)
        db.create_all()
        print("✅ All tables created")
        
        print("\n" + "="*60)
        print("✅ DATABASE RESET COMPLETE!")
        print("="*60)
        print("\nNext steps:")
        print("1. Run: python seed_data_pagination.py")
        print("2. Restart your Flask application")
        print("3. Test endpoints in Postman")
        print()


if __name__ == '__main__':
    reset_database()
