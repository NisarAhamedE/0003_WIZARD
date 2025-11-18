from app.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from datetime import datetime

# Create database session
db = SessionLocal()

try:
    # Check if admin already exists
    admin = db.query(User).filter(User.username == "admin").first()

    if admin:
        print("Admin user already exists, updating password...")
        # Update password
        admin.password_hash = get_password_hash("Admin@123")
        admin.updated_at = datetime.utcnow()
        db.commit()
        print(f"Admin password updated successfully")
    else:
        # Get super_admin role
        super_admin_role = db.query(UserRole).filter(UserRole.name == "super_admin").first()

        if not super_admin_role:
            print("ERROR: super_admin role not found!")
            exit(1)

        # Create admin user
        admin = User(
            username="admin",
            email="admin@wizardplatform.com",
            password_hash=get_password_hash("Admin@123"),
            full_name="Administrator",
            role_id=super_admin_role.id,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(admin)
        db.commit()
        print(f"Admin user created successfully")

    # Verify
    print(f"Username: {admin.username}")
    print(f"Email: {admin.email}")
    print(f"Active: {admin.is_active}")
    print(f"Verified: {admin.is_verified}")
    print(f"Role: {admin.role.name}")
    print(f"Password hash (first 30 chars): {admin.password_hash[:30]}")

finally:
    db.close()
