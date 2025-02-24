from starlette.responses import JSONResponse

from core.i18n import _


def ok(data=None, msg=_("Executing success"), code=0, **kwargs):
    result = {"code": code, "data": data, "msg": msg}
    if kwargs:
        result.update(kwargs)
    return JSONResponse(result)


def failed(data=None, msg=_("Failed to execute"), code=-1, **kwargs):
    result = {"code": code, "data": data, "msg": msg}
    if kwargs:
        result.update(kwargs)
    return JSONResponse(result)
