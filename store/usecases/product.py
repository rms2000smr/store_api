from typing import List
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo
from store.db.mongo import db_client
from store.models.product import ProductModel
from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.core.exceptions import NotFoundException, DuplicateEntryException


class ProductUsecase:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient = db_client.get()
        self.database: AsyncIOMotorDatabase = self.client.get_database()
        self.collection = self.database.get_collection("products")

    async def create(self, body: ProductIn) -> ProductOut:
        
        existing_product = await self.collection.find_one({"name": body.name, "price": body.price})
        if existing_product:
            raise DuplicateEntryException(f"Product with name {body.name} and price {body.price} already exists.")
        
        product_model = ProductModel(**body.model_dump())
        await self.collection.insert_one(product_model.model_dump())

        return ProductOut(**product_model.model_dump())

    async def get(self, id: UUID) -> ProductOut:
        result = await self.collection.find_one({"id": id})

        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        return ProductOut(**result)

    async def query(self, minprice: float = None, maxprice: float = None) -> List[ProductOut]:
        filter = {}

        if minprice is not None and maxprice is not None:
            filter["price"] = {"$gt": minprice, "$lt": maxprice}

        return [ProductOut(**item) async for item in self.collection.find(filter)]

    async def update(self, id: UUID, body: ProductUpdate) -> ProductUpdateOut:
        import datetime

        result = await self.collection.find_one({"id": id})
        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        current_time = datetime.datetime.utcnow()

        update_data = body.model_dump(exclude_none=True)
        update_data["updated_at"] = current_time

        result = await self.collection.find_one_and_update(
            filter={"id": id},
            update={"$set": update_data},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        return ProductUpdateOut(**result)

    async def delete(self, id: UUID) -> bool:
        product = await self.collection.find_one({"id": id})
        if not product:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        result = await self.collection.delete_one({"id": id})

        return True if result.deleted_count > 0 else False


product_usecase = ProductUsecase()
