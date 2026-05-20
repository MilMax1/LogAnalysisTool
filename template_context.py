from pathlib import Path
import csv
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

TEMPLATES_PATH = DATA_DIR / "HDFS.log_templates.csv"


OCCURRENCE_PATH_CANDIDATES = [
    DATA_DIR / "Event_occurrence_matrix.csv"
]


def clean_template(template: str) -> str:
    cleaned = template.replace("[*]", " ... ")
    cleaned = " ".join(cleaned.split())
    return cleaned.strip()


def find_occurrence_matrix_path() -> Path:
    for path in OCCURRENCE_PATH_CANDIDATES:
        if path.exists():
            return path

    expected = " eller ".join(str(path) for path in OCCURRENCE_PATH_CANDIDATES)
    raise FileNotFoundError(
        f"Hittade inte Event_occurrence_matrix.csv. Förväntad plats: {expected}"
    )


def load_event_templates() -> dict[str, str]:
    if not TEMPLATES_PATH.exists():
        raise FileNotFoundError(f"Hittade inte template-filen: {TEMPLATES_PATH}")

    templates: dict[str, str] = {}

    with TEMPLATES_PATH.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            event_id = row["EventId"].strip()
            event_template = clean_template(row["EventTemplate"])
            templates[event_id] = event_template

    return templates


def load_occurrence_row(block_id: str) -> dict[str, str] | None:
    occurrence_path = find_occurrence_matrix_path()

    with occurrence_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["BlockId"].strip() == block_id:
                return row

    return None


def build_template_summary(block_id: str, max_events: int = 30) -> dict[str, Any]:
    templates = load_event_templates()
    occurrence_row = load_occurrence_row(block_id)

    if occurrence_row is None:
        return {
            "block_id": block_id,
            "found": False,
            "events": [],
            "message": "Ingen event occurrence-rad hittades för block-ID.",
        }

    events = []

    for key, value in occurrence_row.items():
        if key in ["BlockId", "Label", "Type"]:
            continue

        if not key.startswith("E"):
            continue

        try:
            count = int(float(value))
        except (TypeError, ValueError):
            continue

        if count <= 0:
            continue

        events.append(
            {
                "event_id": key,
                "count": count,
                "template": templates.get(key, "Okänd event-template"),
            }
        )

    
    events.sort(key=lambda event: event["count"], reverse=True)

    return {
        "block_id": block_id,
        "found": True,
        "events": events[:max_events],
        "total_nonzero_event_types": len(events),
    }


def build_template_context(block_id: str, max_events: int = 30) -> str:
    summary = build_template_summary(block_id, max_events=max_events)

    lines = [
        "Event-template-baserad kontext:",
        "",
        "Viktig tolkning av denna kontext:",
        "- Event templates är härledda från loggraderna och sammanfattar återkommande loggmönster.",
        "- Event counts visar hur många gånger respektive template förekommer för detta block.",
        "- Kontexten innehåller endast event-ID, event counts och event templates som är härledda från loggarna.",
        "- Event counts är inte facit och betyder inte automatiskt att scenariot är Normal eller Anomaly.",
        "",
        f"Block-ID: {block_id}",
    ]

    if not summary["found"]:
        lines.append("- Ingen template-information hittades för detta block.")
        return "\n".join(lines)

    lines.append(
        f"- Antal event-typer med count > 0: {summary['total_nonzero_event_types']}"
    )
    lines.append("")
    lines.append("Event counts:")

    if not summary["events"]:
        lines.append("- Inga event counts över 0 hittades.")
    else:
        for event in summary["events"]:
            lines.append(
                f"- {event['event_id']} | count={event['count']} | "
                f"template={event['template']}"
            )

    return "\n".join(lines)