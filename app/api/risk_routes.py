from fastapi import APIRouter, HTTPException
from app.services.risk import RiskScoring
from app.schemas.risk_asset import AssetRisk
from typing import List

router = APIRouter()
risk_scorer = RiskScoring()

@router.post("/risk/bulk")
async def risk_bulk(assets: List[AssetRisk]):
    try:
        results = []
        for asset in assets:
            res = risk_scorer.cal_risk(asset)
            print(res,'\n')
            results.append(res)

        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

