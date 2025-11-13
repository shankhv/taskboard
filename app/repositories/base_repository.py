from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any


class BaseRepository:
    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str):
        self.db = database
        self.collection = database[collection_name]

    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id": id})

    async def insert_one(self, document: Dict[str, Any]) -> str:
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)