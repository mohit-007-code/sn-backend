import argparse
import asyncio
import sys
from getpass import getpass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.enums.user import UserRole
from app.modules.auth.models import User
from app.modules.users.models import UserProfile
from app.modules.posts.models import Post
from app.modules.comments.models import Comment
from app.modules.likes.models import Like


async def create_or_update_admin(username: str, email: str, password: str, update_if_exists: bool = True):
    username = username.strip().lower()
    email = email.strip().lower()

    async with AsyncSessionLocal() as session:
        # Check if user with email or username exists
        stmt = select(User).where((User.username == username) | (User.email == email))
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()

        if user:
            if not update_if_exists:
                print(f"[!] User with username '{username}' or email '{email}' already exists. Skipping.")
                return False

            print(f"[*] User exists (ID: {user.id}). Updating to ADMIN role and resetting password...")
            user.role = UserRole.ADMIN
            user.hashed_password = hash_password(password)
            user.is_active = True
            await session.commit()
            print(f"[+] Admin account successfully updated!")
            print(f"    Username : {user.username}")
            print(f"    Email    : {user.email}")
            print(f"    Role     : {user.role.value if hasattr(user.role, 'value') else user.role}")
            return True
        else:
            print(f"[*] Creating new admin user '{username}' ({email})...")
            new_user = User(
                username=username,
                email=email,
                hashed_password=hash_password(password),
                role=UserRole.ADMIN,
                is_active=True,
            )
            new_user.profile = UserProfile(full_name="Super Admin")
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            print(f"[+] Admin user successfully created!")
            print(f"    ID       : {new_user.id}")
            print(f"    Username : {new_user.username}")
            print(f"    Email    : {new_user.email}")
            print(f"    Role     : {new_user.role.value if hasattr(new_user.role, 'value') else new_user.role}")
            return True


def main():
    parser = argparse.ArgumentParser(
        description="CLI tool to create or seed Admin users for the Social Platform."
    )
    parser.add_argument(
        "--username",
        "-u",
        type=str,
        default="super@admin.net",
        help="Admin username (default: super@admin.net)",
    )
    parser.add_argument(
        "--email",
        "-e",
        type=str,
        default="super@admin.net",
        help="Admin email (default: super@admin.net)",
    )
    parser.add_argument(
        "--password",
        "-p",
        type=str,
        default="admin@super",
        help="Admin password (default: admin@super)",
    )
    parser.add_argument(
        "--prompt",
        action="store_true",
        help="Prompt interactively for credentials instead of using flags",
    )

    args = parser.parse_args()

    if args.prompt:
        username = input("Enter admin username: ").strip()
        email = input("Enter admin email: ").strip()
        password = getpass("Enter admin password: ").strip()
    else:
        username = args.username
        email = args.email
        password = args.password

    if not username or not email or not password:
        print("[!] Error: Username, email, and password cannot be empty.")
        sys.exit(1)

    asyncio.run(create_or_update_admin(username, email, password))


if __name__ == "__main__":
    main()
