from app.repositories.task_repository import TaskRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.tag_repository import TagRepository
from app.entities.task import Task
from typing import List
from datetime import datetime
from fastapi import HTTPException
import logging
import traceback

logger = logging.getLogger(__name__)


class CreateTaskUseCase:
    def __init__(
            self,
            task_repository: TaskRepository,
            category_repository: CategoryRepository,
            tag_repository: TagRepository
    ):
        self.task_repository = task_repository
        self.category_repository = category_repository
        self.tag_repository = tag_repository

    async def execute(
            self,
            title: str,
            description: str,
            due_date: datetime,
            category_ids: List[str],
            tag_ids: List[str]
    ) -> str:
        """Create task with error handling"""
        try:
            logger.info(f"Creating task: {title}")

            # Validate categories
            for cat_id in category_ids:
                category = await self.category_repository.find_by_id(cat_id)
                if not category:
                    logger.warning(f"Category not found: {cat_id}")
                    raise HTTPException(status_code=404, detail=f"Category '{cat_id}' not found")

            # Validate tags
            for tag_id in tag_ids:
                tag = await self.tag_repository.find_by_id(tag_id)
                if not tag:
                    logger.warning(f"Tag not found: {tag_id}")
                    raise HTTPException(status_code=404, detail=f"Tag '{tag_id}' not found")

            # Create task
            task = Task(title=title, description=description, due_date=due_date)
            task_id = await self.task_repository.create(task.to_dict())

            # Create relationships
            await self.task_repository.add_categories(task_id, category_ids)
            await self.task_repository.add_tags(task_id, tag_ids)

            logger.info(f"Task created successfully: {task_id}")
            return task_id

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in CreateTaskUseCase: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Failed to create task")
