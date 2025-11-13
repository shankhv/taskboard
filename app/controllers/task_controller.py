from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
import logging
import traceback
from app.schemas.task import CreateTaskRequest, TaskResponse, UpdateTaskStatusRequest
from app.schemas.common import PaginatedResponse
from app.use_cases.create_task import CreateTaskUseCase
from app.use_cases.list_tasks import ListTasksUseCase
from app.use_cases.update_task_status import UpdateTaskStatusUseCase
from app.use_cases.delete_task import DeleteTaskUseCase
from app.container import create_container

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_create_task_use_case():
    container = create_container()
    return container.resolve(CreateTaskUseCase)


def get_list_tasks_use_case():
    container = create_container()
    return container.resolve(ListTasksUseCase)


def get_update_task_status_use_case():
    container = create_container()
    return container.resolve(UpdateTaskStatusUseCase)


def get_delete_task_use_case():
    container = create_container()
    return container.resolve(DeleteTaskUseCase)


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
        request: CreateTaskRequest,
        use_case: CreateTaskUseCase = Depends(get_create_task_use_case)
):
    """Create task with error handling"""
    try:
        logger.info(f"Received request to create task: {request.title}")
        task_id = await use_case.execute(
            title=request.title,
            description=request.description,
            due_date=request.due_date,
            category_ids=request.category_ids,
            tag_ids=request.tag_ids
        )
        return TaskResponse(
            id=task_id,
            title=request.title,
            description=request.description,
            due_date=request.due_date,
            status="pending",
            created_at=request.due_date,
            updated_at=request.due_date,
            categories=request.category_ids,
            tags=request.tag_ids
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_task endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to create task")


@router.get("", response_model=PaginatedResponse[TaskResponse])
async def list_tasks(
        category_id: Optional[str] = Query(None),
        tag_id: Optional[str] = Query(None),
        search: Optional[str] = Query(None),
        limit: int = Query(20, ge=1, le=100),
        cursor: Optional[str] = Query(None),
        use_case: ListTasksUseCase = Depends(get_list_tasks_use_case)
):
    """List tasks with error handling"""
    try:
        logger.info("Received request to list tasks")
        tasks, next_cursor = await use_case.execute(
            category_id=category_id,
            tag_id=tag_id,
            search=search,
            limit=limit,
            cursor=cursor
        )

        task_responses = [
            TaskResponse(
                id=task["_id"],
                title=task["title"],
                description=task["description"],
                due_date=task["due_date"],
                status=task["status"],
                created_at=task["created_at"],
                updated_at=task["updated_at"],
                categories=task.get("categories", []),
                tags=task.get("tags", [])
            )
            for task in tasks
        ]

        return PaginatedResponse(items=task_responses, next_cursor=next_cursor)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in list_tasks endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to list tasks")


@router.patch("/{task_id}/status")
async def update_task_status(
        task_id: str,
        request: UpdateTaskStatusRequest,
        use_case: UpdateTaskStatusUseCase = Depends(get_update_task_status_use_case)
):
    """Update task status with error handling"""
    try:
        logger.info(f"Received request to update task {task_id} status")
        await use_case.execute(task_id, request.status)
        return {"success": True, "message": "Task status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_task_status endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to update task status")


@router.delete("/{task_id}")
async def delete_task(
        task_id: str,
        use_case: DeleteTaskUseCase = Depends(get_delete_task_use_case)
):
    """Delete task with error handling"""
    try:
        logger.info(f"Received request to delete task {task_id}")
        await use_case.execute(task_id)
        return {"success": True, "message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_task endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to delete task")