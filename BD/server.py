import uvicorn
from fastapi import FastAPI, Form, Request
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


@app.post('/result')
async def table(request: Request, name: str = Form(...)):
    db: AsyncSession = SessionLocal()
    query = await db.execute(f"""
        SELECT * FROM products
        WHERE name = '{name}'
        ;
    """)
    products = query.all()

    return templates.TemplateResponse('products.html', {"request": request, "products": products})


@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse('search_form.html', {"request": request})


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
