from app.repositories.task_repository import TaskRepository
from app.entities.task import TaskStatus
from fastapi import HTTPException
import logging
import traceback

logger = logging.getLogger(__name__)


class UpdateTaskStatusUseCase:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def execute(self, task_id: str, status: TaskStatus) -> bool:
        """Update task status with error handling"""
        try:
            logger.info(f"Updating task {task_id} status to {status}")
            success = await self.task_repository.update_status(task_id, status)
            if not success:
                logger.warning(f"Task {task_id} not found")
                raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in UpdateTaskStatusUseCase: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Failed to update task status")

