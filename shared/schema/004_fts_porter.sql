-- Rebuild the search index with Porter stemming so that "hangs" matches
-- "hang" and "reading" matches "read". The triggers from 002 keep working:
-- they write to the table by name.
DROP TABLE IF EXISTS bug_records_fts;

CREATE VIRTUAL TABLE bug_records_fts USING fts5(
    symptom,
    root_cause,
    content='bug_records',
    content_rowid='rowid',
    tokenize='porter unicode61'
);

INSERT INTO bug_records_fts(bug_records_fts) VALUES ('rebuild');
