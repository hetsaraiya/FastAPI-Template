from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field


class MandiPrice(BaseModel):
    """
    Schema for daily price of a commodity in a mandi (market).
    """
    state: str
    district: str
    market: str
    commodity: str
    variety: str
    grade: str
    arrival_date: str = Field(..., description="Date in format DD/MM/YYYY")
    min_price: str = Field(..., description="Minimum price in Rupees")
    max_price: str = Field(..., description="Maximum price in Rupees")
    modal_price: str = Field(..., description="Modal (most common) price in Rupees")


class MandiPriceResponse(BaseModel):
    """
    Schema for the response from the Mandi Price API.
    """
    created: int
    updated: int
    created_date: str
    updated_date: str
    active: str
    index_name: str
    org: List[str]
    org_type: str
    source: str
    title: str
    external_ws_url: str
    visualizable: str
    status: str
    total: int
    count: int
    limit: str
    offset: str
    records: List[MandiPrice]