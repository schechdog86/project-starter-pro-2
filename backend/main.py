from fastapi import FastAPI
from backend.app.api import routes
from backend.app.api import auth_routes
from backend.app.api import ai_routes
from backend.app.core.config import settings

app = FastAPI(title="Project Starter Pro 2 API")

app.include_router(routes.router)
app.include_router(auth_routes.router)
app.include_router(ai_routes.router)

@app.get("/")
def root():
    return {"status": "ok", "project": "Project Starter Pro 2"}
