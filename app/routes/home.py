from fastapi import APIRouter, Request

home_route = APIRouter()


@home_route.get('/', tags=['Home'])
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
