from pathlib import Path

def load_log_file(path: str) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Loggfil hittades inte: {path}")

    return file_path.read_text(encoding="utf-8")