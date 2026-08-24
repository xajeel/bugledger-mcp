CREATE TABLE IF NOT EXISTS bug_resolutions (
    record_id   TEXT NOT NULL,
    project     TEXT NOT NULL,
    resolved_at TEXT NOT NULL,
    PRIMARY KEY (record_id, project)
);
