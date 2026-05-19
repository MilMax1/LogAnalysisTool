from pathlib import Path
import csv
import sys

# kör med "python evaluate_classification.py workflow" eller byt ut mot baseline

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def evaluate(method_name: str) -> None:
    summary_path = PROJECT_ROOT / "results" / method_name / "summary.csv"

    if not summary_path.exists():
        raise FileNotFoundError(f"Hittade inte summary.csv: {summary_path}")

    tp = 0
    fp = 0
    fn = 0
    tn = 0
    parse_errors = 0
    total_rows = 0

    with summary_path.open("r", encoding="utf-8", newline="") as summary_file:
        reader = csv.DictReader(summary_file)

        for row in reader:
            total_rows += 1

            ground_truth = row["ground_truth"]
            predicted = row["predicted"]

            if predicted == "PARSE_ERROR":
                parse_errors += 1
                continue

            if ground_truth == "Anomaly" and predicted == "Anomaly":
                tp += 1
            elif ground_truth == "Normal" and predicted == "Anomaly":
                fp += 1
            elif ground_truth == "Anomaly" and predicted == "Normal":
                fn += 1
            elif ground_truth == "Normal" and predicted == "Normal":
                tn += 1

    evaluated = tp + fp + fn + tn

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0
    accuracy = (tp + tn) / evaluated if evaluated else 0

    print(f"{method_name} classification evaluation")
    print("-" * (len(method_name) + 26))
    print(f"Rows in summary: {total_rows}")
    print(f"Evaluated rows:  {evaluated}")
    print(f"Parse errors:    {parse_errors}")
    print()
    print(f"TP: {tp}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print(f"TN: {tn}")
    print()
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"F1-score:  {f1:.3f}")
    print(f"Accuracy:  {accuracy:.3f}")


def main() -> None:
    method_name = "baseline"

    if len(sys.argv) > 1:
        method_name = sys.argv[1]

    evaluate(method_name)


if __name__ == "__main__":
    main()