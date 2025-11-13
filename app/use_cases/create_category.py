from app.repositories.category_repository import CategoryRepository
from app.entities.category import Category
from fastapi import HTTPException
import logging
import traceback

logger = logging.getLogger(__name__)


class CreateCategoryUseCase:
    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    async def execute(self, name: str, description: str = None) -> str:
        """Create category with error handling"""
        try:
            logger.info(f"Creating category: {name}")

            # Check if already exists
            existing = await self.category_repository.find_by_name(name)
            if existing:
                logger.warning(f"Category '{name}' already exists")
                raise HTTPException(status_code=400, detail=f"Category '{name}' already exists")

            category = Category(name=name, description=description)
            category_id = await self.category_repository.create(category.to_dict())
            logger.info(f"Category created successfully: {category_id}")
            return category_id

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in CreateCategoryUseCase: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Failed to create category")
