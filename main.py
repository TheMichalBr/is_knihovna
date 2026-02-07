from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from models.database import Base, engine
from models.models import User, Book, BookCopy, Reservation
from api.routers import auth, books, reservations, admin, users
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Knihovní informační systém")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(reservations.router)
app.include_router(admin.router)
app.include_router(users.router)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    if os.path.exists("templates/index.html"):
        return FileResponse("templates/index.html")
    return {"message": "L: index.html"}

@app.get("/login")
async def login_page():
    if os.path.exists("templates/login.html"):
        return FileResponse("templates/login.html")
    return {"message": "L: login.html"}

@app.get("/catalog")
async def catalog():
    if os.path.exists("templates/catalog.html"):
        return FileResponse("templates/catalog.html")
    return {"message": "L : catalog.html"}

@app.get("/profile")
async def profile():
    if os.path.exists("templates/profile.html"):
        return FileResponse("templates/profile.html")
    return {"message": "L: profile.html"}

@app.get("/admin")
async def admin_panel():
    if os.path.exists("templates/admin.html"):
        return FileResponse("templates/admin.html")
    return {"message": "L: admin.html"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)