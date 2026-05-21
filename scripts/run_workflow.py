from pathlib import Path
import csv
import json
import re
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from workflow import run_workflow  


SCENARIOS_DIR = PROJECT_ROOT / "scenarios"
RESULTS_DIR = PROJECT_ROOT / "results" / "workflow"
METADATA_PATH = SCENARIOS_DIR / "metadata.csv"


SCENARIOS_TO_RUN = None #{"scenario_04", "scenario_05", "scenario_06", "scenario_07"}


def extract_json(text: str) -> dict:
    cleaned = text.strip()

    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise

        return json.loads(match.group(0))


def normalize_label(label: str) -> str:
    label = label.strip().lower()

    if label in ["normal", "normalt"]:
        return "Normal"

    if label in ["anomaly", "anomal", "avvikelse", "abnormal"]:
        return "Anomaly"

    raise ValueError(f"Okänd label/classification: {label}")


def should_run_scenario(scenario_id: str) -> bool:
    if SCENARIOS_TO_RUN is None:
        return True

    return scenario_id in SCENARIOS_TO_RUN


def main() -> None:
    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"Hittade inte metadata.csv: {METADATA_PATH}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    summary_rows = []

    with METADATA_PATH.open("r", encoding="utf-8", newline="") as metadata_file:
        reader = csv.DictReader(metadata_file)

        for row in reader:
            scenario_id = row["scenario_id"]

            if not should_run_scenario(scenario_id):
                continue

            block_id = row["block_id"]
            ground_truth = normalize_label(row["label"])
            numbered_file = row["numbered_file"]
            line_count = int(row["line_count"])

            scenario_path = SCENARIOS_DIR / numbered_file

            if line_count == 0:
                print(f"Hoppar över {scenario_id}: 0 loggrader")
                continue

            log_text = scenario_path.read_text(encoding="utf-8")

            print(f"Kör workflow för {scenario_id} ({ground_truth})...")

            raw_output = run_workflow(
                log_text=log_text,
                scenario_id=scenario_id,
                block_id=block_id,
            )

            raw_output_path = RESULTS_DIR / f"{scenario_id}_raw_output.txt"
            json_output_path = RESULTS_DIR / f"{scenario_id}.json"

            raw_output_path.write_text(raw_output, encoding="utf-8")

            try:
                parsed = extract_json(raw_output)
                predicted = normalize_label(parsed["classification"])
                correct = predicted == ground_truth

                json_output_path.write_text(
                    json.dumps(parsed, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

                summary_rows.append(
                    {
                        "scenario_id": scenario_id,
                        "ground_truth": ground_truth,
                        "predicted": predicted,
                        "correct": correct,
                        "line_count": line_count,
                        "events_count": len(parsed.get("events", [])),
                        "result_file": str(json_output_path.relative_to(PROJECT_ROOT)),
                    }
                )

                print(
                    f"  Ground truth: {ground_truth}, "
                    f"predicted: {predicted}, correct: {correct}"
                )

            except Exception as error:
                print(f"  FEL: Kunde inte tolka JSON för {scenario_id}: {error}")

                summary_rows.append(
                    {
                        "scenario_id": scenario_id,
                        "ground_truth": ground_truth,
                        "predicted": "PARSE_ERROR",
                        "correct": False,
                        "line_count": line_count,
                        "events_count": "",
                        "result_file": str(raw_output_path.relative_to(PROJECT_ROOT)),
                    }
                )

    summary_path = RESULTS_DIR / "summary.csv"

    with summary_path.open("w", encoding="utf-8", newline="") as summary_file:
        fieldnames = [
            "scenario_id",
            "ground_truth",
            "predicted",
            "correct",
            "line_count",
            "events_count",
            "result_file",
        ]

        writer = csv.DictWriter(summary_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"\nKlar. Sammanfattning sparad i: {summary_path}")

    if SCENARIOS_TO_RUN is not None:
        print(f"Körde endast scenarier: {', '.join(sorted(SCENARIOS_TO_RUN))}")


if __name__ == "__main__":
    main()