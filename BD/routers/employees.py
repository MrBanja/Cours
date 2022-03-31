from typing import Optional

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Request, Form, Path, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db
from models import Employee, Shop

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def get_employees(request: Request, db: AsyncSession = Depends(get_db)):
    res = await db.execute(sa.select(Employee))
    employees = res.scalars().all()
    return templates.TemplateResponse('employee.html', {"request": request, "employees": employees})


@router.post("/", response_class=HTMLResponse)
async def add_employee(
        request: Request,
        first_name: str = Form(...),
        second_name: str = Form(...),
        age: int = Form(...),
        shop_id: int = Form(...),
        db: AsyncSession = Depends(get_db),
):
    shop_query = sa.select(Shop).where(Shop.id == shop_id)
    shop: Shop = (await db.execute(shop_query)).scalars().first()
    if not shop:
        return "<script>alert('Wrong shop ID');</script>"

    employee = Employee(first_name=first_name, second_name=second_name, age=age, shop_id=shop_id)
    db.add(employee)
    await db.commit()
    return templates.TemplateResponse('elements/employee_column.html', {"request": request, "employee": employee})


@router.get("/{employee_id}/edit", response_class=HTMLResponse)
async def get_employee_edit_form(
        request: Request,
        employee_id: int = Path(...),
        db: AsyncSession = Depends(get_db),
):
    employee_query = sa.select(Employee).where(Employee.id == employee_id)
    employee: Employee = (await db.execute(employee_query)).scalars().first()
    if not employee:
        raise HTTPException(404, 'Shop not found')

    return templates.TemplateResponse('elements/employee_edit.html', {"request": request, "employee": employee})


@router.get("/{employee_id}", response_class=HTMLResponse)
async def get_employee(
        request: Request,
        employee_id: int = Path(...),
        db: AsyncSession = Depends(get_db),
):
    employee_query = sa.select(Employee).where(Employee.id == employee_id)
    employee: Employee = (await db.execute(employee_query)).scalars().first()
    if not employee:
        raise HTTPException(404, 'Shop not found')

    return templates.TemplateResponse('elements/employee_column.html', {"request": request, "employee": employee})


@router.patch("/{employee_id}", response_class=HTMLResponse)
async def patch_employee(
        request: Request,
        employee_id: int = Path(...),
        first_name: str = Form(...),
        second_name: str = Form(...),
        age: int = Form(...),
        shop_id: int = Form(...),
        db: AsyncSession = Depends(get_db),
):
    employee_query = sa.select(Employee).where(Employee.id == employee_id)
    employee: Employee = (await db.execute(employee_query)).scalars().first()
    if not employee:
        raise HTTPException(404, 'Employee not found')

    if shop_id:
        shop_query = sa.select(Shop).where(Shop.id == shop_id)
        shop: Shop = (await db.execute(shop_query)).scalars().first()
        if not shop:
            return templates.TemplateResponse(
                'elements/employee_column.html',
                {"request": request, "employee": employee, "not_shop_alert": True},
            )
        employee.shop_id = shop_id
    if first_name:
        employee.first_name = first_name
    if second_name:
        employee.second_name = second_name
    if age:
        employee.age = age

    await db.commit()
    return templates.TemplateResponse('elements/employee_column.html', {"request": request, "employee": employee})


@router.delete("/{employee_id}", response_class=HTMLResponse)
async def delete_employee(
        employee_id: int = Path(...),
        db: AsyncSession = Depends(get_db),
):
    employee_query = sa.delete(Employee).where(Employee.id == employee_id)
    await db.execute(employee_query)
    await db.commit()
    return ''
