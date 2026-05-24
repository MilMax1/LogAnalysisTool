from pathlib import Path
import csv
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

TEMPLATES_PATH = DATA_DIR / "HDFS.log_templates.csv"

OCCURRENCE_PATH_CANDIDATES = [
    DATA_DIR / "Event_occurrence_matrix.csv",
    DATA_DIR / "Event_occurance_matrix.csv",
]


NOTABLE_TEMPLATE_IDS = {
    "E7": "writeBlock received exception",
    "E8": "PacketResponder interrupted",
    "E10": "PacketResponder exception",
    "E12": "Exception writing block",
    "E14": "Exception in receiveBlock",
    "E17": "Failed to transfer block",
    "E20": "Unexpected delete error / BlockInfo not found",
    "E24": "Block removed from neededReplications because it does not belong to any file",
    "E28": "addStoredBlock request for block that does not belong to any file",
    "E29": "PendingReplicationMonitor timed out block",
}


COMMON_WARNING_TEMPLATE_IDS = {
    "E4": "Got exception while serving block",
}


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
            "notable_events": [],
            "common_warning_events": [],
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

        event = {
            "event_id": key,
            "count": count,
            "template": templates.get(key, "Okänd event-template"),
        }

        events.append(event)

    
    events.sort(key=lambda event: event["count"], reverse=True)

    notable_events = [
        {
            **event,
            "note": NOTABLE_TEMPLATE_IDS[event["event_id"]],
        }
        for event in events
        if event["event_id"] in NOTABLE_TEMPLATE_IDS
    ]

    common_warning_events = [
        {
            **event,
            "note": COMMON_WARNING_TEMPLATE_IDS[event["event_id"]],
        }
        for event in events
        if event["event_id"] in COMMON_WARNING_TEMPLATE_IDS
    ]

    return {
        "block_id": block_id,
        "found": True,
        "events": events[:max_events],
        "notable_events": notable_events,
        "common_warning_events": common_warning_events,
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
        "- Liknande event templates och counts kan förekomma i både normala och avvikande HDFS-traces.",
        "- Använd därför event counts som stöd för struktur, inte som ensam grund för klassificering.",
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
    lines.append("Särskilt noterbara templates:")

    if not summary["notable_events"]:
        lines.append("- Inga särskilt noterbara templates förekommer i detta block.")
    else:
        for event in summary["notable_events"]:
            lines.append(
                f"- {event['event_id']} | count={event['count']} | "
                f"note={event['note']} | template={event['template']}"
            )

    lines.append("")
    lines.append("Vanliga varnings-/exception-templates som ska tolkas försiktigt:")

    if not summary["common_warning_events"]:
        lines.append("- Inga vanliga varnings-/exception-templates förekommer i detta block.")
    else:
        for event in summary["common_warning_events"]:
            lines.append(
                f"- {event['event_id']} | count={event['count']} | "
                f"note={event['note']} | template={event['template']}"
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