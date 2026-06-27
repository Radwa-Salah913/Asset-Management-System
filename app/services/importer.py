from sqlalchemy.orm import Session
from app.database.models import Asset
from datetime import datetime, UTC

def import_asset(db: Session, asset_data):
    
    existing_asset = (
        db.query(Asset)
        .filter(
            Asset.type == asset_data.type,
            Asset.value == asset_data.value
        )
        .first()
    )
    
    now = datetime.now(UTC)


    if existing_asset:

        existing_asset.last_seen = now
        existing_asset.status = asset_data.status
        existing_asset.source = asset_data.source
        existing_asset.tags = asset_data.tags
        existing_asset.metadata_json = asset_data.metadata

        db.commit()
        db.refresh(existing_asset)

        return existing_asset

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
    db.commit()
    db.refresh(asset)

    return asset