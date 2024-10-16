import uvicorn
import subprocess
from fastapi import FastAPI
from contextlib import asynccontextmanager
from databases.database import init_db
from services.user import create_user, get_all_users
from routes.user import user_route
from routes.service import service_route
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(user_route, prefix='/user')
app.include_router(service_route, prefix='/ml')

app.mount("/static", StaticFiles(directory="webui"), name="static")
templates = Jinja2Templates(directory="webui")

@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return StaticFiles(directory="webui").get_response("favicon.ico")

if __name__ == "__main__":
    uvicorn.run('api:app', host="0.0.0.0", port=8080, reload=True)
