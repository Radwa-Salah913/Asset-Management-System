from sqlalchemy import JSON, Enum, String, Column, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum
import uuid


Base = declarative_base()


class AssetType(str, enum.Enum):
    domain = "domain"
    subdomain = "subdomain"
    ip_address = "ip_address"
    service = "service"
    certificate = "certificate"
    technology = "technology"    


class AssetStatus(str, enum.Enum):
    active = "active"
    stale = "stale"
    archived = "archived"


class AssetRelationship(Base):
    __tablename__ = "asset_relationships"

    id = Column( String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_asset_id = Column( String, ForeignKey("assets.id"), nullable=False)
    target_asset_id = Column( String, ForeignKey("assets.id"), nullable=False)
    relationship_type = Column( String, nullable=False)
    source_asset = relationship(
        "Asset", foreign_keys=[source_asset_id], back_populates="outgoing_relationships"
    )
    target_asset = relationship(
        "Asset", foreign_keys=[target_asset_id], back_populates="incoming_relationships"
    )


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=lambda:str(uuid.uuid4()))
    type = Column(Enum(AssetType), nullable=False)
    value = Column(String, nullable=False)
    status = Column(Enum(AssetStatus), nullable=False)
    first_seen = Column(DateTime,default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    source = Column(String)
    tags = Column(JSON, default=list)
    metadata_json = Column(JSON, default=dict)
    outgoing_relationships = relationship(
        "AssetRelationship", foreign_keys="AssetRelationship.source_asset_id", back_populates="source_asset"
        )
    incoming_relationships = relationship(
        "AssetRelationship", foreign_keys="AssetRelationship.target_asset_id", back_populates="target_asset"
        )

