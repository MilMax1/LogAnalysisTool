from collections import Counter
from typing import Any

from log_parser import parse_log_text

#nuvarande regler och mönster är testvärden ochinte låsta, används för att hitta enkla mönster för att stödja analysen
RULES = {
    "warn_level": ["WARN"],
    "error_level": ["ERROR"],
    "exception": ["Exception", "exception"],
    "failure": ["failed", "failure", "Failed", "Failure"],
    "corruption": ["corrupt", "Corrupt", "corruption"],
    "invalid": ["invalid", "Invalid", "invalidSet"],
    "deletion": ["delete", "deleted", "deleting", "Deleting", "Deleted"],
    "verification": ["verification", "Verification", "verify", "Verify", "Verification succeeded"],
    "block_serving": ["Served block", "Starting thread to transfer block", "Exception in receiveBlock"],
    "block_received": ["Receiving block", "Received block", "BLOCK* NameSystem.addStoredBlock"],
}


def match_rules(parsed_line: dict[str, Any]) -> list[str]:
    matches = []

    level = parsed_line.get("level") or ""
    message = parsed_line.get("message") or ""
    raw = parsed_line.get("raw") or ""

    if level == "WARN":
        matches.append("warn_level")

    if level == "ERROR":
        matches.append("error_level")

    combined_text = f"{message} {raw}"

    for rule_name, keywords in RULES.items():
        if rule_name in ["warn_level", "error_level"]:
            continue

        if any(keyword in combined_text for keyword in keywords):
            matches.append(rule_name)

    return sorted(set(matches))


def get_lines_matching(candidate_events: list[dict[str, Any]], rule_name: str) -> list[int]:
    return [
        event["line_number"]
        for event in candidate_events
        if rule_name in event["matched_rules"]
    ]


def has_sequence(first_lines: list[int], second_lines: list[int]) -> bool:
    if not first_lines or not second_lines:
        return False

    return min(first_lines) < max(second_lines)


def build_pattern_summary(
    parsed_lines: list[dict[str, Any]],
    candidate_events: list[dict[str, Any]],
) -> dict[str, Any]:
    warn_lines = get_lines_matching(candidate_events, "warn_level")
    error_lines = get_lines_matching(candidate_events, "error_level")
    exception_lines = get_lines_matching(candidate_events, "exception")
    failure_lines = get_lines_matching(candidate_events, "failure")
    corruption_lines = get_lines_matching(candidate_events, "corruption")
    invalid_lines = get_lines_matching(candidate_events, "invalid")
    deletion_lines = get_lines_matching(candidate_events, "deletion")
    verification_lines = get_lines_matching(candidate_events, "verification")
    block_serving_lines = get_lines_matching(candidate_events, "block_serving")
    block_received_lines = get_lines_matching(candidate_events, "block_received")

    warning_or_exception_lines = sorted(set(warn_lines + exception_lines))

    pattern_summary = {
        "has_warn": len(warn_lines) > 0,
        "has_error": len(error_lines) > 0,
        "has_exception": len(exception_lines) > 0,
        "has_failure_keyword": len(failure_lines) > 0,
        "has_corruption_keyword": len(corruption_lines) > 0,
        "has_invalid_or_deletion": len(set(invalid_lines + deletion_lines)) > 0,
        "warn_count": len(warn_lines),
        "error_count": len(error_lines),
        "exception_count": len(exception_lines),
        "failure_count": len(failure_lines),
        "corruption_count": len(corruption_lines),
        "invalid_count": len(invalid_lines),
        "deletion_count": len(deletion_lines),
        "verification_count": len(verification_lines),
        "block_serving_count": len(block_serving_lines),
        "block_received_count": len(block_received_lines),
        "warning_or_exception_lines": warning_or_exception_lines,
        "invalid_or_deletion_lines": sorted(set(invalid_lines + deletion_lines)),
    }

    pattern_summary["verification_before_warning_or_exception"] = has_sequence(
        verification_lines,
        warning_or_exception_lines,
    )

    pattern_summary["warning_or_exception_before_invalid_or_deletion"] = has_sequence(
        warning_or_exception_lines,
        sorted(set(invalid_lines + deletion_lines)),
    )

    pattern_summary["received_before_invalid_or_deletion"] = has_sequence(
        block_received_lines,
        sorted(set(invalid_lines + deletion_lines)),
    )

    pattern_summary["possible_sequence_notes"] = build_sequence_notes(pattern_summary)

    return pattern_summary


def build_sequence_notes(pattern_summary: dict[str, Any]) -> list[str]:
    notes = []

    if pattern_summary["has_error"]:
        notes.append(
            "Trace:n innehåller ERROR-rader. Dessa bör granskas som starkare felindikatorer än WARN."
        )

    if pattern_summary["has_warn"] or pattern_summary["has_exception"]:
        notes.append(
            "Trace:n innehåller WARN- och/eller Exception-rader. Dessa är potentiellt relevanta men innebär inte automatiskt anomali."
        )

    if pattern_summary["verification_before_warning_or_exception"]:
        notes.append(
            "Blocket verkar ha verifierats innan senare WARN/Exception-rader uppstår."
        )

    if pattern_summary["warning_or_exception_before_invalid_or_deletion"]:
        notes.append(
            "WARN/Exception-rader förekommer innan blocket markeras som invalid eller raderas."
        )

    if pattern_summary["received_before_invalid_or_deletion"]:
        notes.append(
            "Blocket tas emot eller registreras tidigare i trace:n och markeras senare som invalid eller raderas."
        )

    if pattern_summary["has_corruption_keyword"]:
        notes.append(
            "Trace:n innehåller ord kopplade till corruption/corrupt. Dessa bör granskas särskilt."
        )

    if pattern_summary["has_invalid_or_deletion"]:
        notes.append(
            "Trace:n innehåller invalid/deletion-mönster. Detta kan vara normal blocklivscykel eller relevant för avvikelse beroende på sammanhang."
        )

    if not notes:
        notes.append(
            "Inga tydliga regelbaserade riskmönster identifierades utöver normal loggstruktur."
        )

    return notes


def analyze_with_rules(log_text: str) -> dict[str, Any]:
    parsed_lines = parse_log_text(log_text)

    level_counts = Counter(
        line["level"] if line["level"] else "UNPARSED"
        for line in parsed_lines
    )

    candidate_events = []

    for line in parsed_lines:
        matched_rules = match_rules(line)

        if matched_rules:
            candidate_events.append(
                {
                    "line_number": line["line_number"],
                    "level": line["level"],
                    "component": line["component"],
                    "message": line["message"],
                    "block_id": line["block_id"],
                    "ips": line["ips"],
                    "matched_rules": matched_rules,
                    "raw": line["raw"],
                }
            )

    pattern_summary = build_pattern_summary(parsed_lines, candidate_events)

    return {
        "line_count": len(parsed_lines),
        "parsed_line_count": sum(1 for line in parsed_lines if line["parsed"]),
        "unparsed_line_count": sum(1 for line in parsed_lines if not line["parsed"]),
        "log_level_counts": dict(level_counts),
        "pattern_summary": pattern_summary,
        "candidate_events": candidate_events,
    }


def build_structured_context(
    rule_result: dict[str, Any],
    max_candidate_events: int = 40,
) -> str:
    candidate_events = rule_result["candidate_events"][:max_candidate_events]
    pattern_summary = rule_result["pattern_summary"]

    lines = [
        "Regelbaserad strukturerad kontext:",
        "",
        "Viktig tolkning av denna kontext:",
        "- Denna kontext är stödmaterial, inte facit.",
        "- Matchade regler betyder inte automatiskt att scenariot är en anomali.",
        "- Reglerna markerar rader och mönster som kan vara relevanta att beakta i analysen.",
        "",
        "Översikt:",
        f"- Antal loggrader: {rule_result['line_count']}",
        f"- Parsade loggrader: {rule_result['parsed_line_count']}",
        f"- Ej parsade loggrader: {rule_result['unparsed_line_count']}",
        f"- Log level counts: {rule_result['log_level_counts']}",
        f"- Antal kandidathändelser: {len(rule_result['candidate_events'])}",
        "",
        "Mönstersammanfattning:",
        f"- has_warn: {pattern_summary['has_warn']}",
        f"- has_error: {pattern_summary['has_error']}",
        f"- has_exception: {pattern_summary['has_exception']}",
        f"- has_failure_keyword: {pattern_summary['has_failure_keyword']}",
        f"- has_corruption_keyword: {pattern_summary['has_corruption_keyword']}",
        f"- has_invalid_or_deletion: {pattern_summary['has_invalid_or_deletion']}",
        f"- warn_count: {pattern_summary['warn_count']}",
        f"- error_count: {pattern_summary['error_count']}",
        f"- exception_count: {pattern_summary['exception_count']}",
        f"- invalid_count: {pattern_summary['invalid_count']}",
        f"- deletion_count: {pattern_summary['deletion_count']}",
        f"- verification_count: {pattern_summary['verification_count']}",
        f"- verification_before_warning_or_exception: {pattern_summary['verification_before_warning_or_exception']}",
        f"- warning_or_exception_before_invalid_or_deletion: {pattern_summary['warning_or_exception_before_invalid_or_deletion']}",
        f"- received_before_invalid_or_deletion: {pattern_summary['received_before_invalid_or_deletion']}",
        "",
        "Sekvensnoteringar:",
    ]

    for note in pattern_summary["possible_sequence_notes"]:
        lines.append(f"- {note}")

    lines.extend(
        [
            "",
            "Kandidathändelser:",
        ]
    )

    if not candidate_events:
        lines.append("- Inga kandidathändelser matchade reglerna.")
    else:
        for event in candidate_events:
            lines.append(
                f"- Rad {event['line_number']} | "
                f"level={event['level']} | "
                f"component={event['component']} | "
                f"rules={event['matched_rules']} | "
                f"message={event['message']}"
            )

    if len(rule_result["candidate_events"]) > max_candidate_events:
        lines.append(
            f"- OBS: Endast de första {max_candidate_events} kandidathändelserna visas."
        )

    return "\n".join(lines)