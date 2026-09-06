import re

_WORD_RE = re.compile(r"\w+")


def next_record_id(conn):
    """Returns the next rec_XXXXX id."""

    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT COALESCE(MAX(CAST(substr(id, 5) AS INTEGER)), 0) FROM bug_records"
    ).fetchone()
    next_num = row[0] + 1
    return f"rec_{next_num:05d}"


def count_in_area(conn, feature_area):
    """Counts records in a feature area."""

    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT COUNT(*) FROM bug_records WHERE feature_area = ?",
        (feature_area,),
    ).fetchone()
    return row[0]


def get_bug(conn, record_id):
    """Returns one record id if it exists."""

    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id FROM bug_records WHERE id = ?",
        (record_id,),
    ).fetchone()
    return row


def resolve_bug(conn, record_id, project, resolved_at):
    """Marks a record resolved for one project. Search still returns it."""

    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO bug_resolutions (record_id, project, resolved_at)
        VALUES (?, ?, ?)
        """,
        (record_id, project, resolved_at),
    )
    conn.commit()
    return cursor.rowcount


def update_bug(conn, record_id, fields):
    """Updates the given columns on one record. `fields` keys are trusted
    column names chosen by the caller, never raw user input."""

    if not fields:
        return 0

    columns = list(fields.keys())
    set_clause = ", ".join(f"{column} = ?" for column in columns)
    params = [fields[column] for column in columns] + [record_id]

    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE bug_records SET {set_clause} WHERE id = ?",
        params,
    )
    conn.commit()
    return cursor.rowcount


def delete_bug(conn, record_id):
    """Deletes one record and any resolutions tied to it."""

    cursor = conn.cursor()
    cursor.execute("DELETE FROM bug_resolutions WHERE record_id = ?", (record_id,))
    cursor.execute("DELETE FROM bug_records WHERE id = ?", (record_id,))
    conn.commit()
    return cursor.rowcount


def get_patterns(conn, feature_area, project, limit):
    """Newest records for a feature area, skipping ones resolved for this project."""

    cursor = conn.cursor()
    total = cursor.execute(
        """
        SELECT COUNT(*) FROM bug_records
        WHERE feature_area = ?
        AND id NOT IN (
            SELECT record_id FROM bug_resolutions WHERE project = ?
        )
        """,
        (feature_area, project),
    ).fetchone()[0]
    rows = cursor.execute(
        """
        SELECT id, symptom, root_cause, project, created_at
        FROM bug_records
        WHERE feature_area = ?
        AND id NOT IN (
            SELECT record_id FROM bug_resolutions WHERE project = ?
        )
        ORDER BY created_at DESC, id DESC
        LIMIT ?
        """,
        (feature_area, project, limit),
    ).fetchall()
    return rows, total


def fts_query(text):
    """Turns free text into a safe FTS5 query. Every word is quoted so
    punctuation from pasted error messages cannot break the query syntax,
    and words are joined with OR so any overlap is a hit. FTS5 ranks records
    that share more (and rarer) words first. Returns None when there are no
    usable words."""

    words = []
    for word in _WORD_RE.findall(text):
        word = word.lower()
        if len(word) > 1 and word not in words:
            words.append(word)
    if not words:
        return None
    return " OR ".join(f'"{word}"' for word in words)


def search_bugs(conn, query, feature_area, project, limit):
    """FTS5 search over symptom and root_cause, best matches first."""

    match = fts_query(query)
    if match is None:
        return []

    cursor = conn.cursor()
    sql = """
        SELECT bug_records.id, bug_records.symptom, bug_records.root_cause,
               bug_records.feature_area, bug_records.project,
               bug_records.severity, bug_records.fix_ref, bug_records.created_at
        FROM bug_records_fts
        JOIN bug_records ON bug_records.rowid = bug_records_fts.rowid
        WHERE bug_records_fts MATCH ?
    """
    params = [match]
    if feature_area:
        sql = sql + " AND bug_records.feature_area = ?"
        params.append(feature_area)
    if project:
        sql = sql + " AND bug_records.project = ?"
        params.append(project)
    sql = sql + " ORDER BY bug_records_fts.rank LIMIT ?"
    params.append(limit)

    rows = cursor.execute(sql, params).fetchall()

    hits = []
    for row in rows:
        hits.append(
            {
                "id": row[0],
                "symptom": row[1],
                "root_cause": row[2],
                "feature_area": row[3],
                "project": row[4],
                "severity": row[5],
                "fix_ref": row[6],
                "created_at": row[7],
            }
        )
    return hits


def list_areas(conn):
    """Feature areas and projects with record counts, most records first."""

    cursor = conn.cursor()
    areas = cursor.execute(
        """
        SELECT feature_area, COUNT(*) AS n FROM bug_records
        GROUP BY feature_area ORDER BY n DESC, feature_area
        """
    ).fetchall()
    projects = cursor.execute(
        """
        SELECT project, COUNT(*) AS n FROM bug_records
        GROUP BY project ORDER BY n DESC, project
        """
    ).fetchall()
    total = cursor.execute("SELECT COUNT(*) FROM bug_records").fetchone()[0]
    return areas, projects, total


def insert_bug(
    conn,
    record_id,
    project,
    symptom,
    root_cause,
    feature_area,
    stack,
    severity,
    fix_ref,
    diff_hunk,
    source,
    created_at,
):
    """Inserts a bug record with a caller-chosen id."""

    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO bug_records (
            id, project, symptom, root_cause, feature_area, stack,
            severity, fix_ref, diff_hunk, source, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record_id,
            project,
            symptom,
            root_cause,
            feature_area,
            stack,
            severity,
            fix_ref,
            diff_hunk,
            source,
            created_at,
        ),
    )
    conn.commit()


def create_bug(conn, **fields):
    """Mints the next id and inserts in one write transaction, so two
    sessions recording at the same moment cannot pick the same id."""

    conn.execute("BEGIN IMMEDIATE")
    record_id = next_record_id(conn)
    insert_bug(conn, record_id, **fields)
    return record_id
