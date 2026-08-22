CREATE VIRTUAL TABLE IF NOT EXISTS bug_records_fts USING fts5(
    symptom,
    root_cause,
    content='bug_records',
    content_rowid='rowid'
);

-- Triggers to keep FTS table in sync with bug_records
CREATE TRIGGER IF NOT EXISTS bug_records_ai AFTER INSERT ON bug_records BEGIN
    INSERT INTO bug_records_fts(rowid, symptom, root_cause) 
    VALUES (new.rowid, new.symptom, new.root_cause);
END;

CREATE TRIGGER IF NOT EXISTS bug_records_ad AFTER DELETE ON bug_records BEGIN
    INSERT INTO bug_records_fts(bug_records_fts, rowid, symptom, root_cause) 
    VALUES('delete', old.rowid, old.symptom, old.root_cause);
END;

CREATE TRIGGER IF NOT EXISTS bug_records_au AFTER UPDATE ON bug_records BEGIN
    INSERT INTO bug_records_fts(bug_records_fts, rowid, symptom, root_cause) 
    VALUES('delete', old.rowid, old.symptom, old.root_cause);
    INSERT INTO bug_records_fts(rowid, symptom, root_cause) 
    VALUES (new.rowid, new.symptom, new.root_cause);
END;
