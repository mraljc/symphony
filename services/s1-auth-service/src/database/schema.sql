-- Symphony Users Table
CREATE TABLE symphony_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keycloak_user_id VARCHAR(36) NOT NULL UNIQUE,
    tenant_id UUID NOT NULL,
    symphony_user_preferences JSONB NOT NULL DEFAULT '{}',
    external_app_authorizations JSONB NOT NULL DEFAULT '[]',
    keycloak_sync_version INTEGER DEFAULT 1,
    last_sync_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- External App Authorizations Table
CREATE TABLE external_app_authorizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    keycloak_user_id VARCHAR(36) NOT NULL,
    app_id VARCHAR(50) NOT NULL,
    scopes JSONB NOT NULL DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'active',
    authorized_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ,
    vault_secret_path VARCHAR(500) NOT NULL,
    token_expires_at TIMESTAMPTZ NOT NULL,
    refresh_expires_at TIMESTAMPTZ,
    UNIQUE (tenant_id, keycloak_user_id, app_id)
);

-- Token Revocation Registry Table
CREATE TABLE token_revocation_registry (
    jti VARCHAR(36) PRIMARY KEY,
    keycloak_user_id VARCHAR(36) NOT NULL,
    tenant_id UUID NOT NULL,
    revoked_at TIMESTAMPTZ DEFAULT NOW(),
    revoked_by VARCHAR(50),
    revocation_reason VARCHAR(100),
    token_type VARCHAR(20) DEFAULT 'access',
    expires_at TIMESTAMPTZ NOT NULL
);

-- Token Cache Entries Table
CREATE TABLE token_cache_entries (
    cache_key VARCHAR(500) PRIMARY KEY,
    tenant_id UUID NOT NULL,
    keycloak_user_id VARCHAR(36) NOT NULL,
    app_id VARCHAR(50) NOT NULL,
    token_expiry TIMESTAMPTZ NOT NULL,
    cached_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed TIMESTAMPTZ DEFAULT NOW(),
    access_count INTEGER DEFAULT 0,
    refresh_scheduled_at TIMESTAMPTZ,
    refresh_attempts INTEGER DEFAULT 0,
    vault_secret_path VARCHAR(500) NOT NULL
);

-- Security Events Buffer Table
CREATE TABLE security_events_buffer (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    keycloak_user_id VARCHAR(36),
    event_type VARCHAR(100) NOT NULL,
    event_subtype VARCHAR(100),
    severity VARCHAR(20) DEFAULT 'info',
    ip_address INET,
    user_agent TEXT,
    device_fingerprint VARCHAR(64),
    details JSONB NOT NULL DEFAULT '{}',
    risk_score DECIMAL(4,3) DEFAULT 0.0,
    risk_reasons JSONB DEFAULT '[]',
    processed_by_siem BOOLEAN DEFAULT FALSE,
    siem_processed_at TIMESTAMPTZ,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_symphony_users_keycloak_user ON symphony_users(keycloak_user_id);
CREATE INDEX idx_symphony_users_tenant ON symphony_users(tenant_id);
CREATE INDEX idx_external_apps_tenant_user ON external_app_authorizations(tenant_id, keycloak_user_id);
CREATE INDEX idx_external_apps_token_expiry ON external_app_authorizations(token_expires_at, status);
CREATE INDEX idx_token_revocation_user ON token_revocation_registry(keycloak_user_id, revoked_at);
CREATE INDEX idx_token_revocation_tenant ON token_revocation_registry(tenant_id, revoked_at);
CREATE INDEX idx_token_cache_tenant_user_app ON token_cache_entries(tenant_id, keycloak_user_id, app_id);
CREATE INDEX idx_token_cache_expiry ON token_cache_entries(token_expiry);
CREATE INDEX idx_security_events_tenant ON security_events_buffer(tenant_id, timestamp);
CREATE INDEX idx_security_events_user ON security_events_buffer(keycloak_user_id, timestamp);
CREATE INDEX idx_security_events_siem ON security_events_buffer(processed_by_siem, timestamp);