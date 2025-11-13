from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import traceback
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class CategoryRepository(BaseRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "categories")

    async def create(self, category_dict: Dict[str, Any]) -> str:
        """Create category with error handling"""
        try:
            category_dict["_id"] = str(datetime.utcnow().timestamp()).replace(".", "")
            await self.collection.insert_one(category_dict)
            logger.info(f"Category created: {category_dict['name']} (ID: {category_dict['_id']})")
            return category_dict["_id"]
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find category by name with error handling"""
        try:
            return await self.collection.find_one({"name": name})
        except Exception as e:
            logger.error(f"Error finding category by name '{name}': {str(e)}")
            logger.error(traceback.format_exc())
            raise