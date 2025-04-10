import datetime
import sqlalchemy
from sqlalchemy.orm import Mapped as SQLAlchemyMapped, mapped_column as sqlalchemy_mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import ForeignKey

from src.repository.table import Base

class JwtRecord(Base):
    __tablename__ = "jwt_record"

    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    jwt: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=1024), nullable=False, unique=True, index=True)
    user_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer, nullable=False, index=True)
    
    # Reference to device - now using android_id
    android_id: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=255), 
                                                                ForeignKey("device.android_id"), nullable=True, index=True)
    
    # Token status
    is_blacklisted: SQLAlchemyMapped[bool] = sqlalchemy_mapped_column(sqlalchemy.Boolean, nullable=False, default=False)
    token_type: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=20), nullable=True, default="access")
    
    # Timestamps
    created_at: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(
        sqlalchemy.BigInteger, nullable=False
    )
    updated_at: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(
        sqlalchemy.BigInteger,
        nullable=True,
        server_onupdate=sqlalchemy.text("extract(epoch from now())::bigint"),
    )
    last_used_at: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(
        sqlalchemy.BigInteger, nullable=True
    )
    expires_at: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(
        sqlalchemy.BigInteger, nullable=True
    )
    
    # Relationship with Device model
    device = relationship("Device", back_populates="jwt_records")

    __mapper_args__ = {"eager_defaults": True}