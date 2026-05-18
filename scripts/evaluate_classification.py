from pathlib import Path
import csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = PROJECT_ROOT / "results" / "baseline" / "summary.csv"


def main() -> None:
    if not SUMMARY_PATH.exists():
        raise FileNotFoundError(f"Hittade inte summary.csv: {SUMMARY_PATH}")

    tp = 0
    fp = 0
    fn = 0
    tn = 0
    parse_errors = 0

    with SUMMARY_PATH.open("r", encoding="utf-8", newline="") as summary_file:
        reader = csv.DictReader(summary_file)

        for row in reader:
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

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0
    accuracy = (tp + tn) / (tp + fp + fn + tn) if (tp + fp + fn + tn) else 0

    print("Baseline classification evaluation")
    print("----------------------------------")
    print(f"TP: {tp}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print(f"TN: {tn}")
    print(f"Parse errors: {parse_errors}")
    print()
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"F1-score:  {f1:.3f}")
    print(f"Accuracy:  {accuracy:.3f}")


if __name__ == "__main__":
    main()