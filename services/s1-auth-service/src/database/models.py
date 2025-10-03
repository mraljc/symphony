from sqlalchemy import Column, String, DateTime, JSON, Integer, UUID, Boolean, Text, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class SymphonyUser(Base):
    __tablename__ = "symphony_users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    keycloak_user_id = Column(String(36), unique=True, nullable=False)
    tenant_id = Column(UUID, nullable=False)
    symphony_user_preferences = Column(JSON, nullable=False, default=dict)
    external_app_authorizations = Column(JSON, nullable=False, default=list)
    keycloak_sync_version = Column(Integer, default=1)
    last_sync_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ExternalAppAuthorization(Base):
    __tablename__ = "external_app_authorizations"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID, nullable=False)
    keycloak_user_id = Column(String(36), nullable=False)
    app_id = Column(String(50), nullable=False)
    scopes = Column(JSON, nullable=False, default=list)
    status = Column(String(20), default='active')
    authorized_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True))
    vault_secret_path = Column(String(500), nullable=False)
    token_expires_at = Column(DateTime(timezone=True), nullable=False)
    refresh_expires_at = Column(DateTime(timezone=True))

class TokenRevocation(Base):
    __tablename__ = "token_revocation_registry"

    jti = Column(String(36), primary_key=True)
    keycloak_user_id = Column(String(36), nullable=False)
    tenant_id = Column(UUID, nullable=False)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked_by = Column(String(50))
    revocation_reason = Column(String(100))
    token_type = Column(String(20), default='access')
    expires_at = Column(DateTime(timezone=True), nullable=False)

class TokenCacheEntry(Base):
    __tablename__ = "token_cache_entries"

    cache_key = Column(String(500), primary_key=True)
    tenant_id = Column(UUID, nullable=False)
    keycloak_user_id = Column(String(36), nullable=False)
    app_id = Column(String(50), nullable=False)
    token_expiry = Column(DateTime(timezone=True), nullable=False)
    cached_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())
    access_count = Column(Integer, default=0)
    refresh_scheduled_at = Column(DateTime(timezone=True))
    refresh_attempts = Column(Integer, default=0)
    vault_secret_path = Column(String(500), nullable=False)

class SecurityEvent(Base):
    __tablename__ = "security_events_buffer"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID, nullable=False)
    keycloak_user_id = Column(String(36))
    event_type = Column(String(100), nullable=False)
    event_subtype = Column(String(100))
    severity = Column(String(20), default='info')
    ip_address = Column(String(50))  # Using String for INET for simplicity
    user_agent = Column(Text)
    device_fingerprint = Column(String(64))
    details = Column(JSON, nullable=False, default=dict)
    risk_score = Column(DECIMAL(4, 3), default=0.0)
    risk_reasons = Column(JSON, default=list)
    processed_by_siem = Column(Boolean, default=False)
    siem_processed_at = Column(DateTime(timezone=True))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())