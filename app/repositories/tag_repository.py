from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import traceback
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class TagRepository(BaseRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "tags")

    async def create(self, tag_dict: Dict[str, Any]) -> str:
        """Create tag with error handling"""
        try:
            tag_dict["_id"] = str(datetime.utcnow().timestamp()).replace(".", "")
            await self.collection.insert_one(tag_dict)
            logger.info(f"Tag created: {tag_dict['name']} (ID: {tag_dict['_id']})")
            return tag_dict["_id"]
        except Exception as e:
            logger.error(f"Error creating tag: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find tag by name with error handling"""
        try:
            return await self.collection.find_one({"name": name})
        except Exception as e:
            logger.error(f"Error finding tag by name '{name}': {str(e)}")
            logger.error(traceback.format_exc())
            raise