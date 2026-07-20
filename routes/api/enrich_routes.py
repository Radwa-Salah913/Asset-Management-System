from fastapi import APIRouter,HTTPException
from app.services.enrichment import Enrichment
from app.schemas.enrich_asset import EnrichAsset

router = APIRouter()
enricher = Enrichment()

@router.post("/enrich")
async def enrich_asset(asset : EnrichAsset):
    
    try:
        ans = await enricher.enrich_asset(asset)
        return ans

    except Exception as e:

        raise HTTPException( status_code=500, detail=str(e))

