"""Log line parser supporting structured (JSON) and unstructured (plain text) formats."""

import json
import re
from datetime import datetime
from typing import Optional

# Common unstructured log timestamp patterns
TIMESTAMP_PATTERNS = [
    # ISO 8601: 2024-01-15T13:45:00Z or 2024-01-15T13:45:00.123Z
    (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)', '%Y-%m-%dT%H:%M:%S'),
    # Common log format: 2024-01-15 13:45:00
    (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', '%Y-%m-%d %H:%M:%S'),
    # Apache/nginx: 15/Jan/2024:13:45:00
    (r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})', '%d/%b/%Y:%H:%M:%S'),
    # Syslog: Jan 15 13:45:00
    (r'(\w{3}\s+\d{1,2} \d{2}:\d{2}:\d{2})', '%b %d %H:%M:%S'),
]


def parse_timestamp(raw: str) -> Optional[datetime]:
    """Attempt to parse a raw timestamp string into a datetime object."""
    raw = raw.strip().rstrip('Z')
    formats = [
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%d/%b/%Y:%H:%M:%S',
        '%b %d %H:%M:%S',
        '%b  %d %H:%M:%S',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def extract_timestamp(line: str) -> Optional[datetime]:
    """Extract and parse the first recognisable timestamp from a log line."""
    # Try JSON first
    try:
        data = json.loads(line)
        for key in ('timestamp', 'time', 'ts', '@timestamp', 'date'):
            if key in data:
                return parse_timestamp(str(data[key]))
    except (json.JSONDecodeError, TypeError):
        pass

    # Fall back to regex scanning
    for pattern, _ in TIMESTAMP_PATTERNS:
        match = re.search(pattern, line)
        if match:
            return parse_timestamp(match.group(1))

    return None
