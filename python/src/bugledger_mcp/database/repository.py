def next_record_id(conn):
    """ Returns the next rec_XXXXX id. """

    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT COALESCE(MAX(CAST(substr(id, 5) AS INTEGER)), 0) FROM bug_records"
    ).fetchone()
    next_num = row[0] + 1
    return f"rec_{next_num:05d}"


def count_in_area(conn, feature_area):
    """ Counts records in a feature area. """

    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT COUNT(*) FROM bug_records WHERE feature_area = ?",
        (feature_area,),
    ).fetchone()
    return row[0]


def search_bugs(conn, query, feature_area, project, limit):
    """ FTS5 search over symptom and root_cause. Bad queries return no hits. """

    cursor = conn.cursor()
    sql = """
        SELECT bug_records.id, bug_records.symptom, bug_records.root_cause,
               bug_records.feature_area, bug_records.project,
               bug_records.fix_ref, bug_records.created_at
        FROM bug_records_fts
        JOIN bug_records ON bug_records.rowid = bug_records_fts.rowid
        WHERE bug_records_fts MATCH ?
    """
    params = [query]
    if feature_area:
        sql = sql + " AND bug_records.feature_area = ?"
        params.append(feature_area)
    if project:
        sql = sql + " AND bug_records.project = ?"
        params.append(project)
    sql = sql + " ORDER BY bug_records_fts.rank LIMIT ?"
    params.append(limit)

    try:
        rows = cursor.execute(sql, params).fetchall()
    except Exception:
        return []

    hits = []
    for row in rows:
        hits.append({
            "id": row[0],
            "symptom": row[1],
            "root_cause": row[2],
            "feature_area": row[3],
            "project": row[4],
            "fix_ref": row[5],
            "created_at": row[6],
        })
    return hits



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
    """ Inserts a bug record into the ledger. """

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
