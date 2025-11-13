from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
import logging
import traceback

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None


db = Database()


async def connect_to_mongo():
    """Connect to MongoDB with error handling"""
    try:
        logger.info(f"Connecting to MongoDB at {settings.mongodb_url}")
        db.client = AsyncIOMotorClient(settings.mongodb_url, serverSelectionTimeoutMS=5000)
        db.database = db.client[settings.database_name]

        # Test connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")

        # Create indexes
        await db.database.tasks.create_index("deleted")
        await db.database.tasks.create_index("created_at")
        await db.database.tasks.create_index("due_date")
        await db.database.tasks_categories.create_index([("task_id", 1), ("category_id", 1)])
        await db.database.tasks_tags.create_index([("task_id", 1), ("tag_id", 1)])

        logger.info("Database indexes created successfully")

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        logger.error(traceback.format_exc())
        raise


async def close_mongo_connection():
    """Close MongoDB connection"""
    try:
        if db.client:
            logger.info("Closing MongoDB connection")
            db.client.close()
            logger.info("MongoDB connection closed successfully")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {str(e)}")
        logger.error(traceback.format_exc())


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db.database