from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from datetime import datetime
import base64
import json
import logging
import traceback
from app.repositories.base_repository import BaseRepository
from app.entities.task import TaskStatus

logger = logging.getLogger(__name__)


class TaskRepository(BaseRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "tasks")
        self.tasks_categories = database["tasks_categories"]
        self.tasks_tags = database["tasks_tags"]

    async def create(self, task_dict: Dict[str, Any]) -> str:
        """Create task with error handling"""
        try:
            task_dict["_id"] = str(datetime.utcnow().timestamp()).replace(".", "")
            await self.collection.insert_one(task_dict)
            logger.info(f"Task created: {task_dict['_id']}")
            return task_dict["_id"]
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def add_categories(self, task_id: str, category_ids: List[str]):
        """Add categories to task with error handling"""
        try:
            if category_ids:
                relationships = [{"task_id": task_id, "category_id": cat_id} for cat_id in category_ids]
                await self.tasks_categories.insert_many(relationships)
                logger.info(f"Added {len(category_ids)} categories to task {task_id}")
        except Exception as e:
            logger.error(f"Error adding categories to task {task_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def add_tags(self, task_id: str, tag_ids: List[str]):
        """Add tags to task with error handling"""
        try:
            if tag_ids:
                relationships = [{"task_id": task_id, "tag_id": tag_id} for tag_id in tag_ids]
                await self.tasks_tags.insert_many(relationships)
                logger.info(f"Added {len(tag_ids)} tags to task {task_id}")
        except Exception as e:
            logger.error(f"Error adding tags to task {task_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def find_with_filters(
            self,
            category_id: Optional[str] = None,
            tag_id: Optional[str] = None,
            search: Optional[str] = None,
            limit: int = 20,
            cursor: Optional[str] = None
    ) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """Find tasks with filters and error handling"""
        try:
            query = {"deleted": False}

            # Handle cursor pagination
            if cursor:
                try:
                    cursor_data = json.loads(base64.b64decode(cursor).decode())
                    query["created_at"] = {"$lt": datetime.fromisoformat(cursor_data["created_at"])}
                except Exception as e:
                    logger.warning(f"Invalid cursor: {cursor}")

            # Handle search
            if search:
                query["$or"] = [
                    {"title": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}}
                ]

            # Handle category and tag filters
            task_ids = None

            if category_id:
                cat_relationships = await self.tasks_categories.find(
                    {"category_id": category_id}
                ).to_list(length=None)
                task_ids = {rel["task_id"] for rel in cat_relationships}

                # Early return if no tasks found for this category
                if not task_ids:  # Empty set
                    logger.info(f"No tasks found for category {category_id}")
                    return [], None

            if tag_id:
                tag_relationships = await self.tasks_tags.find(
                    {"tag_id": tag_id}
                ).to_list(length=None)
                tag_task_ids = {rel["task_id"] for rel in tag_relationships}

                # Early return if no tasks found for this tag
                if not tag_task_ids:  # Empty set
                    logger.info(f"No tasks found for tag {tag_id}")
                    return [], None

                # Handle intersection
                if task_ids is not None:
                    task_ids = task_ids.intersection(tag_task_ids)
                    # Early return if intersection is empty
                    if not task_ids:  # Empty set
                        logger.info(f"No tasks found matching both category and tag")
                        return [], None
                else:
                    task_ids = tag_task_ids

            # Apply task_ids filter only if we have valid IDs
            if task_ids is not None:
                # Double check it's not empty before adding to query
                if not task_ids:  # Empty set
                    logger.info("No tasks match the filters")
                    return [], None
                query["_id"] = {"$in": list(task_ids)}

            # Execute query
            tasks = await self.collection.find(query).sort(
                "created_at", -1
            ).limit(limit + 1).to_list(length=limit + 1)

            # Handle pagination cursor
            next_cursor = None
            if len(tasks) > limit:
                tasks = tasks[:limit]
                last_task = tasks[-1]
                cursor_data = {"created_at": last_task["created_at"].isoformat()}
                next_cursor = base64.b64encode(
                    json.dumps(cursor_data).encode()
                ).decode()

            logger.info(f"Found {len(tasks)} tasks")
            return tasks, next_cursor

        except Exception as e:
            logger.error(f"Error finding tasks: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def get_categories_for_task(self, task_id: str) -> List[str]:
        """Get categories for task with error handling"""
        try:
            relationships = await self.tasks_categories.find({"task_id": task_id}).to_list(length=None)
            return [rel["category_id"] for rel in relationships]
        except Exception as e:
            logger.error(f"Error getting categories for task {task_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return []

    async def get_tags_for_task(self, task_id: str) -> List[str]:
        """Get tags for task with error handling"""
        try:
            relationships = await self.tasks_tags.find({"task_id": task_id}).to_list(length=None)
            return [rel["tag_id"] for rel in relationships]
        except Exception as e:
            logger.error(f"Error getting tags for task {task_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return []

    async def update_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update task status with error handling"""
        try:
            result = await self.collection.update_one(
                {"_id": task_id, "deleted": False},
                {"$set": {"status": status, "updated_at": datetime.utcnow()}}
            )
            if result.modified_count > 0:
                logger.info(f"Task {task_id} status updated to {status}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating task {task_id} status: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def soft_delete(self, task_id: str) -> bool:
        """Soft delete task with error handling"""
        try:
            result = await self.collection.update_one(
                {"_id": task_id},
                {"$set": {"deleted": True, "updated_at": datetime.utcnow()}}
            )
            if result.modified_count > 0:
                logger.info(f"Task {task_id} soft deleted")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error soft deleting task {task_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
