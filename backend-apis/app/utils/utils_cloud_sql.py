# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Utils to help with Cloud SQL queries 

"""

import json
import tomllib
from json import JSONDecodeError

import sqlalchemy
from google.cloud.sql.connector.connector import Connector
from sqlalchemy import DECIMAL, Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)
    sql_cfg = config["sql"]

PROJECT_ID = sql_cfg["project"]
REGION = sql_cfg["region"]
INSTANCE_NAME = sql_cfg["instance_name"]
INSTANCE_CONNECTION_NAME = f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}"

DB_USER = sql_cfg["db_user"]
DB_NAME = sql_cfg["db_name"]

# initialize Connector object
connector = Connector()


class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods

    """Base class for ORM"""


class Product(Base):  # pylint: disable=too-few-public-methods

    """Product definition for ORM"""

    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(String(2000))
    image: Mapped[str] = mapped_column(String(300))
    features: Mapped[str] = mapped_column(String(1000))
    categories: Mapped[str] = mapped_column(String(1000))
    price: Mapped[float] = mapped_column(DECIMAL(6, 2))
    quantity: Mapped[int] = mapped_column(Integer)


# function to return the database connection object
def getconn():
    """Gets the DB-API connection to the database

    Returns:
        A DB-API connection to the specified Cloud SQL instance.
    """
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pymysql",
        user=DB_USER,
        enable_iam_auth=True,
        db=DB_NAME,
    )
    return conn


pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)


def get_product(product_id: int) -> Product | None:
    """Gets the product from the database using the id

    Args:
        product_id: int
            id of the product to be queried.

    Returns:
        Product if found or None

    """
    with Session(pool) as session:
        stmt = select(Product).where(Product.id == product_id)
        for row in session.execute(stmt):
            return row[0]
    return None


def convert_product_to_dict(product: Product) -> dict:
    """Converts a product instance to a dict representation.

    Args:
        product: Product
            A Product instance

    Returns:
        dict
            A dict representing the product

    """
    features = []
    if product.features:
        try:
            features = json.loads(product.features.replace("'", '"'))
        except JSONDecodeError as e:
            print(e)

    categories = []
    if product.categories:
        try:
            categories = json.loads(product.categories.replace("'", '"'))
        except JSONDecodeError as e:
            print(e)

    return_dict = {
        "id": int(product.id),
        "title": str(product.title),
        "description": str(product.description),
        "image": str(product.image),
        "features": features,
        "categories": categories,
        "price": float(product.price),
        "quantity": int(product.quantity),
    }
    return return_dict


def get_random_products(size: int = 10) -> list[dict]:
    """Gets random products from the database and returns
       a list of dicts representing the products

    Args:
        size: int
            Size of the list to return

    Returns:
        list[dict]
            A list of dict representations of random products

    """
    results = []
    with Session(pool) as session:
        # select Product order by RAND() limit to size
        stmt = select(Product).order_by(sqlalchemy.func.rand()).limit(size)
        for row in session.execute(stmt):
            results.append(convert_product_to_dict(row[0]))
    return results


def get_products(id_list: list) -> list[dict]:
    """Gets a list of products from the database and
       returns a list of dicts representing the products

    Args:
        id_list: list
            list of ids to be queried in the database

    Returns:
        list[dict]
            A list of dict representations of random products


    """
    results = []
    with Session(pool) as session:
        # select Product where id in id_list
        stmt = select(Product).where(Product.id.in_(id_list))
        for row in session.execute(stmt):
            results.append(convert_product_to_dict(row[0]))
    return results
