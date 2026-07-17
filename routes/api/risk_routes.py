from fastapi import APIRouter, HTTPException
from app.services.risk import RiskScoring
from app.schemas.risk_asset import AssetRisk
from typing import List

router = APIRouter()
risk_scorer = RiskScoring()

@router.post("/risk/bulk")
async def risk_bulk(assets: List[AssetRisk]):
    
    results = []
    for asset in assets:
        try:
            res = risk_scorer.cal_risk(asset)
            print(res,'\n')

        except Exception as e:
            res = {
                "error": str(e),
                "asset": asset.model_dump()
            }
        results.append(res)
        
    return {"results": results}


