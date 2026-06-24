from sqlalchemy.orm import Session
from app.database.models import Asset



def import_asset(db: Session, asset_data):
    
    existing_asset = (
        db.query(Asset)
        .filter(
            Asset.type == asset_data.type,
            Asset.value == asset_data.value
        )
        .first()
    )

    if existing_asset:
        return existing_asset

    asset = Asset(
        id=asset_data.id,
        type=asset_data.type,
        value=asset_data.value,
        status=asset_data.status,
        source=asset_data.source,
        tags=asset_data.tags,
        metadata_json=asset_data.metadata
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)

    return asset