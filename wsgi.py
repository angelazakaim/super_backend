import os
from app import create_app

# Render provides 'postgres://', but SQLAlchemy requires 'postgresql://'
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
    os.environ["DATABASE_URL"] = uri

# Create the app with the production config
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == "__main__":
    app.run()