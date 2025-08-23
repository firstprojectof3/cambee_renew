CREATE SCHEMA IF NOT EXISTS app;

CREATE TABLE IF NOT EXISTS app.notice_raw (
  id BIGSERIAL PRIMARY KEY,
  url TEXT NOT NULL,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status TEXT NOT NULL,
  html TEXT,
  error TEXT
);

CREATE TABLE IF NOT EXISTS app.notice (
  id BIGSERIAL PRIMARY KEY,
  url TEXT NOT NULL UNIQUE,
  url_key TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  body  TEXT NOT NULL,
  category TEXT,
  posted_at DATE,
  checksum TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notice_posted_at ON app.notice(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_notice_category ON app.notice(category);
