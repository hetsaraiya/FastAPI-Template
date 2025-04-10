from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status

from src.api.dependencies.auth import consumer_or_farmer_required 
from src.api.dependencies.repository import get_repository
from src.external.gov.client import DataGovClient
from src.models.schemas.mandi import MandiPriceResponse
from src.models.db.user import User, UserTypeEnum
from src.utilities.logging.logger import logger

router = APIRouter(
    prefix="/mandi",
    tags=["mandi"],
    responses={404: {"description": "Not found"}},
)


@router.get("/prices", response_model=MandiPriceResponse)
async def get_mandi_prices(
    current_user: User = Depends(consumer_or_farmer_required),
    format: str = Query("json", description="Output format (json, xml, or csv)"),
    offset: int = Query(0, description="Number of records to skip for pagination"),
    limit: int = Query(10, description="Maximum number of records to return"),
    state: Optional[str] = Query(None, description="Filter by state"),
    district: Optional[str] = Query(None, description="Filter by district"),
    market: Optional[str] = Query(None, description="Filter by market"),
    commodity: Optional[str] = Query(None, description="Filter by commodity"),
    variety: Optional[str] = Query(None, description="Filter by variety"),
    grade: Optional[str] = Query(None, description="Filter by grade"),
):
    """
    Get current daily price of various commodities from various markets (Mandi).
    """
    try:
        async with DataGovClient() as client:
            response = await client.get_mandi_prices(
                format=format,
                offset=offset,
                limit=limit,
                state=state,
                district=district,
                market=market,
                commodity=commodity,
                variety=variety,
                grade=grade
            )
            return response
    except Exception as e:
        logger.error(f"Error fetching mandi prices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch mandi prices: {str(e)}"
        )