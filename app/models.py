from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    description: str
    price: int = Field(ge=0)
    currency: str = "VND"
    stock: int = Field(ge=0)
    accent: str


class ProductList(BaseModel):
    items: list[Product]
