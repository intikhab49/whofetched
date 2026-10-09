-- One row per request that reaches the Worker.
CREATE TABLE IF NOT EXISTS hits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,              -- epoch ms when the Worker received the request
  method TEXT,
  host TEXT,
  path TEXT,
  query TEXT,
  status INTEGER,
  mode TEXT,                        -- c | blocked | forbidden | robots | home | other
  token TEXT,                       -- canary token from the path, if any
  ip TEXT,
  asn INTEGER,
  as_org TEXT,
  country TEXT,
  region TEXT,
  city TEXT,
  colo TEXT,
  http_protocol TEXT,
  tls_version TEXT,
  tls_cipher TEXT,
  client_tcp_rtt INTEGER,
  ua TEXT,
  accept TEXT,
  accept_language TEXT,
  accept_encoding TEXT,
  referer TEXT,
  from_hdr TEXT,
  via TEXT,
  sec_ch_ua TEXT,
  sec_ch_ua_platform TEXT,
  sec_fetch_site TEXT,
  sec_fetch_mode TEXT,
  sec_fetch_dest TEXT,
  signature_agent TEXT,             -- Web Bot Auth headers, stored raw for offline verification
  signature_input TEXT,
  signature TEXT,
  headers_json TEXT                 -- all headers except cookie/authorization
);
CREATE INDEX IF NOT EXISTS hits_token ON hits(token);
CREATE INDEX IF NOT EXISTS hits_ts ON hits(ts);
