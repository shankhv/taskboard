from fastapi import APIRouter, Depends, HTTPException
import logging
import traceback
from app.schemas.tag import CreateTagRequest, TagResponse
from app.use_cases.create_tag import CreateTagUseCase
from app.container import create_container

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tags", tags=["tags"])

def get_create_tag_use_case():
    container = create_container()
    return container.resolve(CreateTagUseCase)


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(
    request: CreateTagRequest,
    use_case: CreateTagUseCase = Depends(get_create_tag_use_case)
):
    """Create tag with error handling"""
    try:
        logger.info(f"Received request to create tag: {request.name}")
        tag_id = await use_case.execute(request.name)
        return TagResponse(id=tag_id, name=request.name)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_tag endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to create tag")