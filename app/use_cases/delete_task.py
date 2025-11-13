from app.repositories.task_repository import TaskRepository
from fastapi import HTTPException
import logging
import traceback

logger = logging.getLogger(__name__)


class DeleteTaskUseCase:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def execute(self, task_id: str) -> bool:
        """Delete task with error handling"""
        try:
            logger.info(f"Deleting task: {task_id}")
            success = await self.task_repository.soft_delete(task_id)
            if not success:
                logger.warning(f"Task {task_id} not found")
                raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
            logger.info(f"Task deleted successfully: {task_id}")
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in DeleteTaskUseCase: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Failed to delete task")