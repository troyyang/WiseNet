from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select, or_, func
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import make_transient

import core.database as db
from core.i18n import _
from core.security import hash_password_md5, create_access_token
from models.models import User
from schemas.user import UserCreate, UserLogin, UserList, UserSecuritySetting


class UserService:
    def __init__(self):
        pass

    async def register_user(self, user: UserCreate):
        if not user.username:
            raise ValueError(_("Username must be provided."))

        if not user.email:
            raise ValueError(_("Email must be provided."))

        if not user.password:
            raise ValueError(_("Password must be provided."))

        async with db.get_async_session() as session:
            try:
                result = await session.execute(select(User).filter(User.username == user.username))
                db_user = result.scalar_one_or_none()
                if db_user:
                    raise HTTPException(status_code=400, detail=_("Username already registered"))

                hashed_password = hash_password_md5(user.password)
                new_user = User(username=user.username, email=user.email, mobile=user.mobile, hashed_password=hashed_password)
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
            except IntegrityError:
                raise HTTPException(status_code=400, detail=_("The user already exists, please check the username, email or mobile."))
            except Exception:
                raise HTTPException(status_code=500, detail=_("Failed to register user"))
                
        return new_user

    async def login_user(self, user: UserLogin):
        # Query the database to check if the user exists based on username, email, or mobile
        query = text("SELECT * FROM users WHERE username = :identifier OR email = :identifier OR mobile = :identifier")
        async with db.get_async_session() as session:
            result = await session.execute(query, {'identifier': user.username})
            result = result.one_or_none()
        if result:
            # Logic for successful login (e.g., password verification) goes here
            if not (hash_password_md5(user.password) == result.hashed_password):
                raise HTTPException(status_code=400, detail=_("Username or password is incorrect"))

            access_token = create_access_token(data={"userid": result.id})
            
            return {"token": access_token}
        raise HTTPException(status_code=400, detail={"error": _("Invalid credentials")})

    async def find(self, condition: UserList, expunge: bool = True):
        async with db.get_async_session() as session:
            # Start building the query
            query = select(User)
            count_query = select(func.count()).select_from(User)
            
            # Apply filters based on the condition
            if condition.keyword:
                query = query.where(
                    or_(
                        User.username.ilike(f"%{condition.keyword}%"),
                        User.email.ilike(f"%{condition.keyword}%"),
                        User.mobile.ilike(f"%{condition.keyword}%")
                    )
                )

            if condition.role:
                query = query.where(User.role == condition.role)
                count_query = count_query.where(User.role == condition.role)

            # if condition.start_time:
            #     query = query.where(User.create_time >= condition.start_time)
            # if condition.end_time:
            #     query = query.where(User.create_time <= condition.end_time)
            
            # Add ordering and execute the query
            query = query.order_by(User.update_time.desc())
            # Implement pagination
            offset = (condition.current - 1) * condition.page_size
            query = query.offset(offset).limit(condition.page_size)
            
            result = await session.execute(query)
            count_result = await session.execute(count_query)
            
            # Extract the results as a list of User objects
            users = result.scalars().all()
            total_count = count_result.scalar()
            if users and expunge:
                for user in users:
                    make_transient(user)
            return users, total_count


    async def find_by_name(self, username: str, expunge: bool = True):
        async with db.get_async_session() as session:
            result = await session.execute(select(User).filter(User.username == username))
            user = result.scalar_one_or_none()
            if user and expunge:
                    make_transient(user)
        if user:
            return user
        raise HTTPException(status_code=404, detail=_("User not found"))

    async def find_by_id(self, user_id: int, expunge: bool = True):
        async with db.get_async_session() as session:
            result = await session.execute(select(User).filter(User.id == user_id))
            if result:
                user = result.scalar_one_or_none()
                if user and expunge:
                    make_transient(user)
        if not user:
            raise HTTPException(status_code=404, detail=_("User not found"))
        return user


    async def save_user(self, user: UserCreate) -> User | None:
        """
        Update a user in the database.

        Args:
            user (UserCreate): The user object to update.

        Returns:
            User | None: The updated user object, or None if the user was not found.       
        """
        if not user.username:
            raise ValueError(_("Username must be provided."))

        if not user.email:
            raise ValueError(_("Email must be provided."))

        async with db.get_async_session() as session:   
            if not user.id:
                return await self.register_user(user)
            try:
                result = await session.execute(select(User).filter(User.id == user.id))
                entry = result.scalar_one_or_none()
                if not entry:
                    raise ValueError(_("User not found."))

                entry.username = user.username
                entry.email = user.email
                entry.mobile = user.mobile
                if user.password:
                    entry.hashed_password = hash_password_md5(user.password)
                entry.update_time = datetime.now()

                await session.commit()
                make_transient(entry)
                return entry
            except IntegrityError:
                raise HTTPException(status_code=400, detail=_("The user already exists, please check the username, email or mobile."))
            except Exception:
                raise HTTPException(status_code=500, detail=_("Failed to update user"))

    async def delete_user(self, user_id: int) -> User | None:
        """
        Delete a user from the database.

        Args:
            user_id (int): The ID of the user to delete.

        Returns:
            User | None: The deleted user object, or None if the user was not found.
        """
        async with db.get_async_session() as session:   
            result = await session.execute(select(User).filter(User.id == user_id))
            entry = result.scalar_one_or_none()
            if not entry:
                raise ValueError(_("User not found."))

            await session.delete(entry)
            await session.commit()
            make_transient(entry)
            return entry

    async def update_user_password(self, user_id: int, userSecurity: UserSecuritySetting) -> User | None:
        """
        Update user password in the database.
        """
        if not userSecurity.org_password:
            raise ValueError(_("Original password must be provided."))

        if not userSecurity.new_password:
            raise ValueError(_("New password must be provided."))

        if not userSecurity.confirm_password:
            raise ValueError(_("Confirm password must be provided."))

        if userSecurity.new_password != userSecurity.confirm_password:
            raise ValueError(_("New password and confirm password must be the same."))

        async with db.get_async_session() as session:   
            result = await session.execute(select(User).filter(User.id == user_id))
            entry = result.scalar_one_or_none()
            if not entry:
                raise ValueError(_("User not found."))

            if entry.hashed_password != hash_password_md5(userSecurity.org_password):
                raise ValueError(_("Original password is incorrect."))

            entry.hashed_password = hash_password_md5(userSecurity.new_password)
            entry.update_time = datetime.now()

            await session.commit()
            make_transient(entry)
            return entry