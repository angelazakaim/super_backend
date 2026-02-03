import os
from dotenv import load_dotenv # Add this
load_dotenv()                 # Add this
from app import create_app

# Handle different database URL formats
uri = os.getenv("DATABASE_URL")

if uri:
    # Only convert PostgreSQL URLs (Render/Heroku compatibility)
    if uri.startswith("postgres://") and not uri.startswith("postgresql://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
        os.environ["DATABASE_URL"] = uri
else:
    # Fallback for local safety if ENV is missing
    os.environ["DATABASE_URL"] = "sqlite:///instance/ecommerce_dev.db"

# Create the app with the production config
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == "__main__":
    app.run()