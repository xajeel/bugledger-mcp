CREATE TABLE IF NOT EXISTS bug_records (
    id           TEXT PRIMARY KEY,      -- rec_00001
    project      TEXT NOT NULL,
    symptom      TEXT NOT NULL,         -- what was observed (searchable)
    root_cause   TEXT NOT NULL,         -- why it happened (the lesson; quality bar)
    feature_area TEXT NOT NULL,         -- auth, payments, uploads... (retrieval key)
    stack        TEXT,                  -- JSON array: ["fastapi", "react"]
    severity     TEXT,                  -- low | medium | high
    fix_ref      TEXT,                  -- commit hash / PR url
    diff_hunk    TEXT,                  -- the fix's code change (capped ~32KB) — raw
    source       TEXT NOT NULL,         -- slash | confirm | import — capture channel
    created_at   TEXT NOT NULL
);
