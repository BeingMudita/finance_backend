from app.database import Base, engine, SessionLocal
from app.services.user_service import UserService
from app.config import settings

def init():
    print("🚀 Creating database...")

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("👤 Creating admin user...")
        UserService(db).ensure_admin_exists(
            email=settings.FIRST_ADMIN_EMAIL,
            password=settings.FIRST_ADMIN_PASSWORD,
        )
        print("✅ Done!")
    finally:
        db.close()

if __name__ == "__main__":
    init()