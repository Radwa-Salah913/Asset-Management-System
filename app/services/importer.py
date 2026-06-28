from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.models import Asset
from datetime import datetime, UTC
from app.database.models import AssetStatus
from app.schemas.asset import AssetImport
from typing import Any, Dict, List
from pydantic import ValidationError


def import_asset(db: Session, asset_data: AssetImport):

    
    # Check first if this asset already exist based on type & value to prevent duplication.
    existing_asset = (
        db.query(Asset)
        .filter(
            Asset.type == asset_data.type,
            Asset.value == asset_data.value
        )
        .first()
    )
    
    now = datetime.now(UTC)

    # update old asset by new data.
    if existing_asset:

        # update last_seen with the current time of import.  
        existing_asset.last_seen = now
        
        # update status to active bec. asset appear again.
        existing_asset.status = AssetStatus.active
        existing_asset.source = asset_data.source

        # merge old tags with new tags and save all. 
        merged_tags = list( set((existing_asset.tags or []) + (asset_data.tags or [])))
        existing_asset.tags = merged_tags

        # merge metadata tags with new metadata and save all. 
        merged_metadata = {
            **(existing_asset.metadata_json or {}),
            **(asset_data.metadata or {})
        }      
        existing_asset.metadata_json = merged_metadata


        return False
    
    # else 
    asset = Asset(
        
        type=asset_data.type,
        value=asset_data.value,
        status=asset_data.status,
        source=asset_data.source,
        tags=asset_data.tags,
        metadata_json=asset_data.metadata,
        first_seen=now,
        last_seen=now
    )

    db.add(asset)

    return True


# record number of skiped, updated and, Inserted assets , and return summary.
def import_assets_batch(db: Session, asset_data: List[Dict[str,Any]]):
    imported = 0
    updated = 0
    skipped = 0
    errors = []

    for index, raw_asset in enumerate(asset_data):

        try:

            # Validate each one independly.
            asset = AssetImport.model_validate(raw_asset)

            created = import_asset(db, asset)

            if created:
                imported += 1
            else:
                updated += 1

        except ValidationError as e:

            skipped += 1

            errors.append(
                {
                    "index": index,
                    "asset": raw_asset,
                    "reason": e.errors(),
                }
            )

        except SQLAlchemyError as e:

            db.rollback()

            skipped += 1

            errors.append(
                {
                    "index": index,
                    "asset": raw_asset,
                    "reason": str(e),
                }
            )

    try:
        # commit all data once.
        db.commit()

    except SQLAlchemyError as e:

        db.rollback()

        raise RuntimeError(f"Batch import failed: {e}")

    return {
        "summary": {
            "imported": imported,
            "updated": updated,
            "skipped": skipped,
            "total": len(asset_data),
        },
        "errors": errors,
    }

   
    
