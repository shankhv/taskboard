from app.repositories.tag_repository import TagRepository
from app.entities.tag import Tag
from fastapi import HTTPException
import logging
import traceback

logger = logging.getLogger(__name__)


class CreateTagUseCase:
    def __init__(self, tag_repository: TagRepository):
        self.tag_repository = tag_repository

    async def execute(self, name: str) -> str:
        """Create tag with error handling"""
        try:
            logger.info(f"Creating tag: {name}")

            # Check if already exists
            existing = await self.tag_repository.find_by_name(name)
            if existing:
                logger.warning(f"Tag '{name}' already exists")
                raise HTTPException(status_code=400, detail=f"Tag '{name}' already exists")

            tag = Tag(name=name)
            tag_id = await self.tag_repository.create(tag.to_dict())
            logger.info(f"Tag created successfully: {tag_id}")
            return tag_id

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in CreateTagUseCase: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Failed to create tag")
