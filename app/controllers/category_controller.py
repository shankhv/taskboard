from fastapi import APIRouter, Depends, HTTPException
import logging
import traceback
from app.schemas.category import CreateCategoryRequest, CategoryResponse
from app.use_cases.create_category import CreateCategoryUseCase
from app.container import create_container

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/categories", tags=["categories"])

def get_create_category_use_case():
    container = create_container()
    return container.resolve(CreateCategoryUseCase)


@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(
    request: CreateCategoryRequest,
    use_case: CreateCategoryUseCase = Depends(get_create_category_use_case)
):
    """Create category with error handling"""
    try:
        logger.info(f"Received request to create category: {request.name}")
        category_id = await use_case.execute(request.name, request.description)
        return CategoryResponse(id=category_id, name=request.name, description=request.description)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_category endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to create category")
