import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from log_parser import parse_log_line, parse_log_file

input_path = "scenarios/scenario_10_raw.txt"
output_path = "parsedLogs/scenario_10_parsed.json"

parsed_logs = parse_log_file(input_path)

result = {
    "input_file": input_path,
    "line_count": len(parsed_logs),
    "parsed_count": sum(1 for log in parsed_logs if log["parsed"]),
    "unparsed_count": sum(1 for log in parsed_logs if not log["parsed"]),
    "logs": parsed_logs,
}

Path(output_path).write_text(
    json.dumps(result, indent=2),
    encoding="utf-8"
)

print(f"Parsed {result['parsed_count']} of {result['line_count']} lines")
print(f"Saved result to {output_path}")