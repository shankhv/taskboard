from punq import Container
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.task_repository import TaskRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.tag_repository import TagRepository
from app.use_cases.create_task import CreateTaskUseCase
from app.use_cases.list_tasks import ListTasksUseCase
from app.use_cases.update_task_status import UpdateTaskStatusUseCase
from app.use_cases.delete_task import DeleteTaskUseCase
from app.use_cases.create_category import CreateCategoryUseCase
from app.use_cases.create_tag import CreateTagUseCase
from app.database import get_database


def create_container() -> Container:
    container = Container()

    # Register database
    container.register(AsyncIOMotorDatabase, factory=get_database)

    # Register repositories
    container.register(TaskRepository)
    container.register(CategoryRepository)
    container.register(TagRepository)

    # Register use cases
    container.register(CreateCategoryUseCase)
    container.register(CreateTagUseCase)
    container.register(CreateTaskUseCase)
    container.register(ListTasksUseCase)
    container.register(UpdateTaskStatusUseCase)
    container.register(DeleteTaskUseCase)

    return container