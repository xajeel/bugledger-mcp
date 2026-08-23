import re


def error_texts():
    """ Error messages the agent sees when record_bug is rejected. """

    ROOT_CAUSE_TOO_SHORT = (
        "root_cause is too vague. Write at least 20 characters explaining WHY "
        "it happened, not what you changed. 'fixed it' is not a root cause."
    )
    INVALID_SEVERITY = "severity must be one of: low, medium, high."
    INVALID_SOURCE = "source must be one of: slash, confirm, import."
    return ROOT_CAUSE_TOO_SHORT, INVALID_SEVERITY, INVALID_SOURCE


def allowed_values():
    """ Allowed field values for record_bug. """

    SEVERITY_VALUES = ["low", "medium", "high"]
    SOURCE_VALUES = ["slash", "confirm", "import"]
    MIN_ROOT_CAUSE_LEN = 20
    return SEVERITY_VALUES, SOURCE_VALUES, MIN_ROOT_CAUSE_LEN


def diff_settings():
    """ Limits and patterns for capturing a fix diff. """

    DIFF_CAP = 32 * 1024
    TRUNCATION_MARK = "\n\n[truncated — diff exceeded 32KB]"
    COMMIT_HASH_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
    return DIFF_CAP, TRUNCATION_MARK, COMMIT_HASH_RE


def search_settings():
    """ Limits for search_bugs. """

    SEARCH_LIMIT = 10
    return SEARCH_LIMIT

