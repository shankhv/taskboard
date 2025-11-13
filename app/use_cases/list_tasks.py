from app.repositories.task_repository import TaskRepository
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
import logging
import traceback

logger = logging.getLogger(__name__)


class ListTasksUseCase:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def execute(
            self,
            category_id: Optional[str] = None,
            tag_id: Optional[str] = None,
            search: Optional[str] = None,
            limit: int = 20,
            cursor: Optional[str] = None
    ) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """List tasks with error handling"""
        try:
            logger.info(f"Listing tasks - category: {category_id}, tag: {tag_id}, search: {search}")

            tasks, next_cursor = await self.task_repository.find_with_filters(
                category_id=category_id,
                tag_id=tag_id,
                search=search,
                limit=limit,
                cursor=cursor
            )

            # Enrich tasks
            for task in tasks:
                task["categories"] = await self.task_repository.get_categories_for_task(task["_id"])
                task["tags"] = await self.task_repository.get_tags_for_task(task["_id"])

            logger.info(f"Retrieved {len(tasks)} tasks")
            return tasks, next_cursor

        except Exception as e:
            logger.error(f"Error in ListTasksUseCase: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Failed to list tasks")
