from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

def setup_error_handlers(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 401:
            if "text/html" in request.headers.get("accept", ""):
                return RedirectResponse(url="/login")
            return JSONResponse(status_code=401, content={"error": "Unauthorized"})
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})