"""
CREATE ADMIN USER SCRIPT

This script will either:
1. Create a new admin user, OR
2. Make an existing user an admin

Usage:
    python3 create_admin.py
"""

from app.db.session import engine, SessionLocal
from app.models.user import User, UserProfile
from app.utils.auth import hash_password
from sqlalchemy.orm import Session
from datetime import datetime

def list_users(db: Session):
    """List all existing users"""
    users = db.query(User).all()
    if not users:
        print("\n❌ No users found in database.")
        return []

    print("\n📋 Existing Users:")
    for user in users:
        admin_badge = "👑 ADMIN" if user.is_admin else ""
        print(f"  {user.id}. {user.username} ({user.email}) {admin_badge}")
    return users

def make_user_admin(db: Session, user_id: int):
    """Make an existing user an admin"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        print(f"\n❌ User with ID {user_id} not found.")
        return False

    user.is_admin = True
    db.commit()
    print(f"\n✅ {user.username} is now an admin!")
    return True

def create_new_admin_user(db: Session, username: str, email: str, password: str):
    """Create a new admin user"""
    # Check if user already exists
    existing = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()

    if existing:
        print(f"\n❌ User already exists: {existing.username} ({existing.email})")
        return False

    # Create user
    hashed_password = hash_password(password)
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=True,  # Auto-verify admin
        is_admin=True,  # Make them admin
        created_at=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create profile
    profile = UserProfile(user_id=new_user.id)
    db.add(profile)
    db.commit()

    print(f"\n✅ Admin user created successfully!")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"\n🔐 Login at: http://localhost:8080/login.html")
    return True

def main():
    print("=" * 60)
    print("🛠️  ADMIN USER CREATOR")
    print("=" * 60)

    db = SessionLocal()

    try:
        # List existing users
        users = list_users(db)

        print("\n" + "=" * 60)
        print("Choose an option:")
        print("  1. Make an existing user admin")
        print("  2. Create a new admin user")
        print("=" * 60)

        choice = input("\nEnter choice (1 or 2): ").strip()

        if choice == "1":
            if not users:
                print("\n❌ No users available. Please create a new admin user instead.")
                return

            user_id = input("Enter user ID to make admin: ").strip()
            try:
                user_id = int(user_id)
                make_user_admin(db, user_id)
            except ValueError:
                print("\n❌ Invalid user ID. Must be a number.")

        elif choice == "2":
            print("\n📝 Create New Admin User")
            print("-" * 40)
            username = input("Username: ").strip()
            email = input("Email: ").strip()
            password = input("Password: ").strip()

            if not username or not email or not password:
                print("\n❌ All fields are required.")
                return

            create_new_admin_user(db, username, email, password)

        else:
            print("\n❌ Invalid choice. Please enter 1 or 2.")

    finally:
        db.close()

if __name__ == "__main__":
    main()
