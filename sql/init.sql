CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id UUID PRIMARY KEY,
    source_file TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    total_rows INTEGER NOT NULL DEFAULT 0,
    clean_rows INTEGER NOT NULL DEFAULT 0,
    quarantined_rows INTEGER NOT NULL DEFAULT 0,
    quality_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    summary TEXT
);

CREATE TABLE IF NOT EXISTS clean_orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    order_ts TIMESTAMPTZ NOT NULL,
    product_category TEXT NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    quantity INTEGER NOT NULL,
    country TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    source_file TEXT NOT NULL,
    run_id UUID NOT NULL REFERENCES pipeline_runs(run_id),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quarantined_records (
    quarantine_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES pipeline_runs(run_id),
    source_file TEXT NOT NULL,
    row_number INTEGER NOT NULL,
    raw_record JSONB NOT NULL,
    errors JSONB NOT NULL,
    repair_hint TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quality_checks (
    check_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES pipeline_runs(run_id),
    check_name TEXT NOT NULL,
    status TEXT NOT NULL,
    failed_rows INTEGER NOT NULL DEFAULT 0,
    details TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS repair_suggestions (
    suggestion_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES pipeline_runs(run_id),
    severity TEXT NOT NULL,
    issue_type TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    example_fix TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clean_orders_run_id ON clean_orders(run_id);
CREATE INDEX IF NOT EXISTS idx_quarantine_run_id ON quarantined_records(run_id);
CREATE INDEX IF NOT EXISTS idx_quality_run_id ON quality_checks(run_id);
