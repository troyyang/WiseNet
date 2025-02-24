from fastapi import APIRouter, HTTPException, Depends
from jwt import PyJWTError

from core.error_handle import AuthorizationException
from core.i18n import _
from core.middleware import login_required
from core.extends_logger import logger
from schemas.result import ok, failed
from services.user_service import UserService
from schemas.user import UserCreate, UserList


router = APIRouter()

def get_user_service():
    return UserService()

@router.post("/list")
async def user_list(condition: UserList, user: dict = Depends(login_required), user_service: UserService = Depends(get_user_service)):
    try:
        userid = user.get('userid')
        if userid:
            user = await user_service.find_by_id(userid)
            if not user or not user.role == 'ADMIN':
                raise AuthorizationException(code=401, msg=_("Unauthorized"))

            users, total = await user_service.find(condition)
            return ok({
                        "total": total,
                        "list": [user.to_dict(filter=["id","username", "email", "mobile", "role","create_time", "update_time"]) for user in users]})
    except HTTPException as e:
        return failed(data=None, msg=e.detail)
    except Exception as e:
        logger.error(f"user_list error: {e}")
        return failed(data=None, msg=str(e))


@router.put("")
async def user_save(data: UserCreate, user: dict = Depends(login_required), user_service: UserService = Depends(get_user_service)):
    try:
        userid = user.get('userid')
        if userid:
            user = await user_service.find_by_id(userid)
            if not user or not user.role == 'ADMIN':
                raise AuthorizationException(code=401, msg=_("Unauthorized"))

            user = await user_service.save_user(data)
            return ok(user.to_dict(filter=["id","username", "email", "mobile", "role","create_time", "update_time"]))
    except HTTPException as e:
        return failed(data=None, msg=e.detail)
    except Exception as e:
        logger.error(f"user_save error: {e}")
        return failed(data=None, msg=str(e))


@router.delete("/{user_id}")
async def user_delete(user_id: int, user: dict = Depends(login_required), user_service: UserService = Depends(get_user_service)):
    try:
        userid = user.get('userid')
        if userid:
            user = await user_service.find_by_id(userid)
            if not user or not user.role == 'ADMIN':
                raise AuthorizationException(code=401, msg=_("Unauthorized"))

            await user_service.delete_user(user_id)
            return ok({"success": True})
    except HTTPException as e:
        return failed(data=None, msg=e.detail)
    except Exception as e:
        logger.error(f"user_delete error: {e}")
        return failed(data=None, msg=str(e))