from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, conint
from typing import Optional, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from task1_price_gap.price_gap import find_price_gap_pair

router = APIRouter()

class PriceGapRequest(BaseModel):
    nums: List[int]
    k: conint(ge=0)

class PriceGapResponse(BaseModel):
    indices: Optional[List[int]] = None
    values: Optional[List[int]] = None
    message: str

@router.post("/price-gap-pair", response_model=PriceGapResponse)
async def find_price_gap_pair_endpoint(request: PriceGapRequest):
    """
    Find lexicographically smallest pair of indices (i, j) where 
    i < j and abs(nums[i] - nums[j]) == k
    """
    try:
        # Validate that nums has at least 0 elements (no minimum requirement)
        result = find_price_gap_pair(request.nums, request.k)
        
        if result is None:
            return PriceGapResponse(
                indices=None,
                values=None,
                message="No valid pair found"
            )
        
        i, j = result
        return PriceGapResponse(
            indices=[i, j],
            values=[request.nums[i], request.nums[j]],
            message="Valid pair found"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")