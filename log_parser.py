import re
from pathlib import Path
from typing import Any


BLOCK_ID_PATTERN = re.compile(r"\bblk_-?\d+\b")
IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b")

NUMBERED_LINE_PATTERN = re.compile(
    r"^\[(?P<numbered_line>\d+)\]\s+(?P<log_content>.*)$"
)

LOG_LINE_PATTERN = re.compile(
    r"^(?P<date>\d{6})\s+"
    r"(?P<time>\d{6})\s+"
    r"(?P<thread>\d+)\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"(?P<component>[^:]+):\s+"
    r"(?P<message>.*)$"
)


def extract_block_id(text: str) -> str | None:
    match = BLOCK_ID_PATTERN.search(text)

    if not match:
        return None

    return match.group(0)


def extract_ips(text: str) -> list[str]:
    return IP_PATTERN.findall(text)


def strip_number_prefix(line: str) -> tuple[str, int | None]:
    match = NUMBERED_LINE_PATTERN.match(line)

    if not match:
        return line, None

    numbered_line = int(match.group("numbered_line"))
    log_content = match.group("log_content")

    return log_content, numbered_line


def parse_log_line(line: str, file_line_number: int) -> dict[str, Any]:
    original_line = line
    log_content, numbered_line = strip_number_prefix(line)

    line_number = numbered_line if numbered_line is not None else file_line_number

    match = LOG_LINE_PATTERN.match(log_content)

    if not match:
        return {
            "line_number": line_number,
            "file_line_number": file_line_number,
            "numbered_line": numbered_line,
            "date": None,
            "time": None,
            "thread": None,
            "level": None,
            "component": None,
            "message": log_content,
            "block_id": extract_block_id(log_content),
            "ips": extract_ips(log_content),
            "raw": original_line,
            "raw_without_prefix": log_content,
            "parsed": False,
        }

    data = match.groupdict()
    message = data["message"]

    return {
        "line_number": line_number,
        "file_line_number": file_line_number,
        "numbered_line": numbered_line,
        "date": data["date"],
        "time": data["time"],
        "thread": data["thread"],
        "level": data["level"],
        "component": data["component"],
        "message": message,
        "block_id": extract_block_id(message),
        "ips": extract_ips(message),
        "raw": original_line,
        "raw_without_prefix": log_content,
        "parsed": True,
    }


def parse_log_text(log_text: str) -> list[dict[str, Any]]:
    parsed_logs = []

    for file_line_number, line in enumerate(log_text.splitlines(), start=1):
        if not line.strip():
            continue

        parsed_logs.append(parse_log_line(line, file_line_number))

    return parsed_logs


def parse_log_file(path: str) -> list[dict[str, Any]]:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Log file not found: {path}")

    log_text = file_path.read_text(encoding="utf-8")
    return parse_log_text(log_text)