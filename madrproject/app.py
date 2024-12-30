from fastapi import FastAPI

from madrproject.accounts.routers import router as account_router
from madrproject.auth.routers import router as auth_router
from madrproject.books.routers import router as books_router
from madrproject.novelists.routers import router as novelists_router

app = FastAPI()
app.include_router(router=account_router)
app.include_router(router=auth_router)
app.include_router(router=books_router)
app.include_router(router=novelists_router)


@app.get('/')
def read_root():
    return {'message': 'Olá Mundo'}
