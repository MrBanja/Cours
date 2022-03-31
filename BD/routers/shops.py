from typing import Optional

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Request, Form, Path, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db
from models import Shop

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def get_shops(request: Request, db: AsyncSession = Depends(get_db)):
    res = await db.execute(sa.select(Shop))
    shops = res.scalars().all()
    return templates.TemplateResponse('shop.html', {"request": request, "shops": shops})


@router.post("/", response_class=HTMLResponse)
async def add_shop(
        request: Request,
        name: str = Form(...),
        address: str = Form(...),
        db: AsyncSession = Depends(get_db),
):
    shop = Shop(address=address, name=name)
    db.add(shop)
    await db.commit()
    return templates.TemplateResponse('elements/shop_column.html', {"request": request, "shop": shop})


@router.get("/{shop_id}/edit", response_class=HTMLResponse)
async def get_shop(
        request: Request,
        shop_id: int = Path(...),
        db: AsyncSession = Depends(get_db),
):
    shop_query = sa.select(Shop).where(Shop.id == shop_id)
    shop: Shop = (await db.execute(shop_query)).scalars().first()
    if not shop:
        raise HTTPException(404, 'Shop not found')

    return templates.TemplateResponse('elements/shop_edit.html', {"request": request, "shop": shop})


@router.get("/{shop_id}", response_class=HTMLResponse)
async def get_shop(
        request: Request,
        shop_id: int = Path(...),
        db: AsyncSession = Depends(get_db),
):
    shop_query = sa.select(Shop).where(Shop.id == shop_id)
    shop: Shop = (await db.execute(shop_query)).scalars().first()
    if not shop:
        raise HTTPException(404, 'Shop not found')

    return templates.TemplateResponse('elements/shop_column.html', {"request": request, "shop": shop})


@router.patch("/{shop_id}", response_class=HTMLResponse)
async def patch_shop(
        request: Request,
        shop_id: int = Path(...),
        name: Optional[str] = Form(None),
        address: Optional[str] = Form(None),
        db: AsyncSession = Depends(get_db),
):
    shop_query = sa.select(Shop).where(Shop.id == shop_id)
    shop: Shop = (await db.execute(shop_query)).scalars().first()
    if not shop:
        raise HTTPException(404, 'Shop not found')
    if name:
        shop.name = name
    if address:
        shop.address = address

    await db.commit()
    return templates.TemplateResponse('elements/shop_column.html', {"request": request, "shop": shop})


@router.delete("/{shop_id}", response_class=HTMLResponse)
async def delete_shop(
        shop_id: int = Path(...),
        db: AsyncSession = Depends(get_db),
):
    shop_query = sa.delete(Shop).where(Shop.id == shop_id)
    await db.execute(shop_query)
    await db.commit()
    return ''
