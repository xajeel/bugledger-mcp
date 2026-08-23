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
