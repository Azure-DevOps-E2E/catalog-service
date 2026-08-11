from app.models import Product


class ProductRepository:
    def __init__(self) -> None:
        self._products = (
            Product(
                id="prd-001",
                name="Mechanical Keyboard",
                description="Compact 75% layout with tactile switches.",
                price=1_290_000,
                stock=10,
                accent="amber",
            ),
            Product(
                id="prd-002",
                name="Studio Headphones",
                description="Closed-back headphones tuned for focused work.",
                price=2_150_000,
                stock=7,
                accent="violet",
            ),
            Product(
                id="prd-003",
                name="Desk Light Mini",
                description="Warm dimmable light with a minimal footprint.",
                price=780_000,
                stock=14,
                accent="mint",
            ),
            Product(
                id="prd-004",
                name="Everyday Backpack",
                description="Weather-resistant 18L pack for a daily setup.",
                price=1_680_000,
                stock=5,
                accent="sky",
            ),
            Product(
                id="prd-005",
                name="Ceramic Travel Mug",
                description="Double-wall mug with a soft-touch sleeve.",
                price=420_000,
                stock=20,
                accent="coral",
            ),
        )

    def find_all(self) -> list[Product]:
        return list(self._products)

    def find_by_id(self, product_id: str) -> Product | None:
        return next((item for item in self._products if item.id == product_id), None)
