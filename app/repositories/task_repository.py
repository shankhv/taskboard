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
            """Find tasks with filters, search, and cursor-based pagination."""
            try:
                query: Dict[str, Any] = {"deleted": False}

                # 1️⃣ Cursor-based pagination
                if cursor:
                    try:
                        cursor_data = json.loads(base64.b64decode(cursor).decode())
                        cursor_date = datetime.fromisoformat(cursor_data["created_at"])
                        query["created_at"] = {"$lt": cursor_date}
                    except Exception:
                        logger.warning(f"Invalid cursor: {cursor}")

                # 2️⃣ Keyword search
                if search:
                    query["$or"] = [
                        {"title": {"$regex": search, "$options": "i"}},
                        {"description": {"$regex": search, "$options": "i"}}
                    ]

                # 3️⃣ Filter by category/tag relationships
                task_ids: Optional[set] = None

                if category_id:
                    cat_relationships = await self.tasks_categories.find(
                        {"category_id": category_id}
                    ).to_list(length=None)

                    cat_task_ids = {rel["task_id"] for rel in cat_relationships}
                    if not cat_task_ids:
                        logger.info(f"No tasks found for category {category_id}")
                        return [], None

                    task_ids = cat_task_ids

                if tag_id:
                    tag_relationships = await self.tasks_tags.find(
                        {"tag_id": tag_id}
                    ).to_list(length=None)

                    tag_task_ids = {rel["task_id"] for rel in tag_relationships}
                    if not tag_task_ids:
                        logger.info(f"No tasks found for tag {tag_id}")
                        return [], None

                    # If both filters exist, intersect sets
                    if task_ids is not None:
                        task_ids &= tag_task_ids
                        if not task_ids:
                            logger.info("No tasks match both category and tag filters")
                            return [], None
                    else:
                        task_ids = tag_task_ids

                # 4️⃣ Apply filtered task IDs to query
                if task_ids is not None:
                    if not task_ids:
                        logger.info("No matching task IDs after filtering")
                        return [], None
                    query["_id"] = {"$in": list(task_ids)}

                # 5️⃣ Query tasks collection
                tasks = await self.collection.find(query).sort(
                    "created_at", -1
                ).limit(limit + 1).to_list(length=limit + 1)

                # 6️⃣ Generate next cursor
                next_cursor = None
                if len(tasks) > limit:
                    tasks = tasks[:limit]
                    last_task = tasks[-1]
                    created_at = last_task.get("created_at")
                    if created_at:
                        cursor_data = {"created_at": created_at.isoformat()}
                        next_cursor = base64.b64encode(
                            json.dumps(cursor_data).encode()
                        ).decode()

                logger.info(f"Found {len(tasks)} tasks (next_cursor={next_cursor})")
                return tasks, next_cursor

            except Exception as e:
                logger.error(f"Error finding tasks: {e}")
                logger.debug(traceback.format_exc())
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
        """Soft delete a task (mark deleted=True) with detailed logging"""
        try:
            # Always ensure string type
            task_id = str(task_id).strip()
            logger.info(f"Attempting to soft delete task: '{task_id}'")

            # Step 1: Check if the task exists
            existing_task = await self.collection.find_one({"_id": task_id})
            if not existing_task:
                logger.warning(f"No task found with _id='{task_id}'")
                return False

            logger.info(f"Found task: {existing_task}")

            # Step 2: Check if already deleted
            if existing_task.get("deleted", False):
                logger.warning(f"Task '{task_id}' is already deleted")
                return False

            # Step 3: Perform soft delete
            result = await self.collection.update_one(
                {"_id": task_id},
                {"$set": {"deleted": True, "updated_at": datetime.utcnow()}}
            )

            # Step 4: Verify update result
            if result.modified_count == 1:
                logger.info(f"Task '{task_id}' soft deleted successfully")
                return True
            else:
                logger.warning(
                    f"Task '{task_id}' matched but not modified. "
                    f"matched_count={result.matched_count}, modified_count={result.modified_count}"
                )
                updated = await self.collection.find_one({"_id": task_id})
                logger.debug(f"Task after update attempt: {updated}")
                return False

        except Exception as e:
            logger.error(f"Error soft deleting task '{task_id}': {e}")
            logger.error(traceback.format_exc())
            raise
