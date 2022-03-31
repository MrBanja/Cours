import sqlalchemy as sa

from database import Base


class Shop(Base):
    __tablename__ = "shop"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    address = sa.Column(sa.String, nullable=False)

    sqlite_autoincrement = True
    __mapper_args__ = {"eager_defaults": True}


class Employee(Base):
    __tablename__ = "employee"

    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.String, nullable=False)
    second_name = sa.Column(sa.String, nullable=False)
    age = sa.Column(sa.Integer, nullable=False)

    shop_id = sa.Column(sa.ForeignKey(Shop.id, ondelete='set null'), nullable=False)
