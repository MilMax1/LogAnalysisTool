from typing import List, Dict, Any

Rule = Dict[str, Any]
ParsedLog = Dict[str, Any]
DetectedEvent = Dict[str, Any]

RULES: List[Rule] = [

        {
        "id": "E4",
        "type": "Exception while serving",
        "severity": "medium",
        "field": "message",
        "contains": ["exception"],
        "description": "Got exception while serving"
         },
         {
        "id": "E7",
        "type": "writeBlock received exception",
        "severity": "medium",
        "field": "message",
        "contains": ["writeBlock", "exception"],
        "description": "writeBlock received exception"

        },
        {
        "id": "E8",
        "type": "PacketResponder interrupted",
        "severity": "medium",
        "field": "message",
        "contains": ["PacketResponder", "Interrupted"],
        "description": "PacketResponder Interrupted"
        },
        {
            "id": "E10",
            "type": "PacketResponder exception",
            "severity": "medium",
            "field": "message",
            "contains": ["PacketResponder", "exception"],
            "description": "PacketResponder exception"
        },
        {
            "id":"E12",
            "type": "Exception writing block",
            "severity": "medium",
            "field": "message",
            "contains": ["Exception writing block"],
            "description": "Exception writing block"
        },
        {
            "id":"E14",
            "type": "Exception in receiveBlock",
            "severity": "medium",
            "field": "message",
            "contains": ["Exception in receiveBlock"],
            "description": "Exception in receiveBlock for block"
        },
        {
            "id":"E17",
            "type": "Failed to trans",
            "severity": "medium",
            "field": "message",
            "contains": ["Failed to transfer"],
            "description": "Failed to transfer block"
        },
        {
            "id":"E20",
            "type": "BlockInfo not found",
            "severity": "medium",
            "field": "message",
            "contains": ["error"],
            "description": "Unexpected error trying to delete block"
        },
        {
            "id":"E29",
            "type": "PendingReplicationMonitor timed out block",
            "severity": "medium",
            "field": "message",
            "contains": ["PendingReplicationMonitor", "timed out"],
            "description": "PendingReplicationMonitor timed out block"
        }
]     

def rule_matches(log: ParsedLog, rule: Rule) -> bool:
    field_name = rule.get("field", "message")
    field_value = str(log.get(field_name, "")).lower()

    contains = rule.get("contains", [])

    if contains:
        return all(term.lower() in field_value for term in contains)
    return False

def detect_events(logs: List[ParsedLog]) -> List[DetectedEvent]:
    events: List[DetectedEvent] = []

    for log in logs:
        for rule in RULES:
            if rule_matches(log, rule):
                events.append({
                    "rule_id": rule["id"],
                    "type": rule["type"],
                    "severity": rule["severity"],
                    "description": rule["description"],
                    "log_entry": log
                })
    
    return events


def summarize_events(events: List[DetectedEvent]) -> List[Dict[str, Any]]:
    grouped: Dict[str, Dict[str, Any]] = {}

    for event in events:
        key = event["type"]

        if key not in grouped:
            grouped[key] = {
                "type": event["type"],
                "severity": event["severity"],
                "count": 0,
                "lines": [],
                "examples": [],
                "description": event["description"]
            }

        grouped[key]["count"] += 1

        if event.get("line_number") is not None:
            grouped[key]["lines"].append(event["line_number"])

        if len(grouped[key]["examples"]) < 3:
            grouped[key]["examples"].append({
                "line_number": event.get("line_number"),
                "message": event.get("message")
            })

    return list(grouped.values())


def analyze_with_rules(parsed_logs: List[ParsedLog]) -> Dict[str, Any]:
    events = detect_events(parsed_logs)
    summary = summarize_events(events)

    return {
        "matched_event_count": len(events),
        "event_types": len(summary),
        "events": events,
        "summary": summary
    }