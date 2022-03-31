import logging
from typing import Optional

import sqlalchemy as sa
import uvicorn
from fastapi import FastAPI, Request, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.templating import Jinja2Templates

from dependencies import get_db
from models import Shop, Employee
from routers.employees import router as employee_router
from routers.shops import router as shop_router

app = FastAPI()
app.include_router(
    shop_router,
    prefix='/shops'
)
app.include_router(
    employee_router,
    prefix='/employees'
)

templates = Jinja2Templates(directory="templates")


@app.get('/')
async def index(
        request: Request,
        db: AsyncSession = Depends(get_db),
):
    resp_q = sa.select([Employee, Shop]).select_from(Shop).join(Employee)
    resp = await db.execute(resp_q)
    return templates.TemplateResponse('main.html', {'request': request, 'data': resp.all()})


@app.post('/search')
async def index(
        request: Request,
        first_name: Optional[str] = Form(None),
        age_from: Optional[int] = Form(None),
        age_to: Optional[int] = Form(None),
        db: AsyncSession = Depends(get_db),
):
    resp_q = sa.select([Employee, Shop]).select_from(Shop).join(Employee)
    if first_name is not None:
        resp_q = resp_q.where(Employee.first_name.like(f'%{first_name}%'))
    if age_from is not None:
        resp_q = resp_q.where(Employee.age >= age_from)
    if age_to is not None:
        resp_q = resp_q.where(Employee.age <= age_to)

    resp = await db.execute(resp_q)
    return templates.TemplateResponse('elements/main_search_table.html', {'request': request, 'data': resp.all()})


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
