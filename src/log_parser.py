import re
from pathlib import Path

BLOCK_ID_PATTERN = re.compile(r"\bblk_-?\d+\b")
IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b")

LOG_LINE_PATTERN = re.compile(
    r"^(?P<date>\d{6})\s+"
    r"(?P<time>\d{6})\s+"
    r"(?P<thread>\d+)\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"(?P<component>[^:]+):\s+"
    r"(?P<message>.*)$"
)

def extract_block_id(message: str) -> str | None:
    match = BLOCK_ID_PATTERN.search(message)

    if not match:
        return None
    
    return match.group(0)


def extract_ips(message: str) -> list[str]:
    return IP_PATTERN.findall(message)

def parse_log_line(line: str, line_number: int) -> dict:
    match = LOG_LINE_PATTERN.match(line)

    if not match:
        return {
            "line_number": line_number,
            "date": None,
            "time": None,
            "thread": None,
            "level": None,
            "component": None,
            "message": line,
            "block_id": extract_block_id(line),
            "ips": extract_ips(line),
            "raw": line,
            "parsed": False,
        }

    data = match.groupdict()
    message = data["message"]

    return {
        "line_number": line_number,
        "date": data["date"],
        "time": data["time"],
        "thread": data["thread"],
        "level": data["level"],
        "component": data["component"],
        "message": message,
        "block_id": extract_block_id(message),
        "ips": extract_ips(message),
        "raw": line,
        "parsed": True,
    }

def parse_log_text(log_text: str) -> list[dict]:
    parsed_logs = []

    for line_number, line in enumerate(log_text.splitlines(), start=1):
        if not line.strip():
            continue

        parsed_logs.append(parse_log_line(line, line_number))

    return parsed_logs

def parse_log_file(path: str) -> list[dict]:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Log file not found: {path}")

    log_text = file_path.read_text(encoding="utf-8")
    return parse_log_text(log_text)
