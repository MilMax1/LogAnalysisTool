from pathlib import Path
import csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HDFS_LOG_PATH = PROJECT_ROOT / "data" / "HDFS.log"
SCENARIOS_DIR = PROJECT_ROOT / "scenarios"

# scenarion slumpmässigt valda med 50% normal och 50% anomaly 
SCENARIOS = [
    ("scenario_01", "blk_-1608999687919862906", "Normal"),
    ("scenario_02", "blk_7503483334202473044", "Normal"),
    ("scenario_03", "blk_-9073992586687739851", "Normal"),
    ("scenario_04", "blk_7854771516489510256", "Normal"),
    ("scenario_05", "blk_1717858812220360316", "Normal"),
    ("scenario_06", "blk_-3544583377289625738", "Anomaly"),
    ("scenario_07", "blk_-8531310335568756456", "Anomaly"),
    ("scenario_08", "blk_3947106522258141922", "Anomaly"),
    ("scenario_09", "blk_7956543127401791181", "Anomaly"),
    ("scenario_10", "blk_-3102267849859399193", "Anomaly"),
    ("scenario_11", "blk_4237356440788557206", "Normal"),
    ("scenario_12", "blk_5668708402864483965", "Normal"),
    ("scenario_13", "blk_-4334049176684001514", "Normal"),
    ("scenario_14", "blk_709268592365361671", "Normal"),
    ("scenario_15", "blk_-7042855855719423267", "Normal"),
    ("scenario_16", "blk_6248210333079836276", "Anomaly"),
    ("scenario_17", "blk_6331191059322192725", "Anomaly"),
    ("scenario_18", "blk_8240042894352190894", "Anomaly"),
    ("scenario_19", "blk_6426032162622263299", "Anomaly"),
    ("scenario_20", "blk_5133973138291673173", "Anomaly"),
]

def number_log_lines(lines: list[str]) -> str:
    return "\n".join(
        f"[{index + 1}] {line}"
        for index, line in enumerate(lines)
    )


def main() -> None:
    if not HDFS_LOG_PATH.exists():
        raise FileNotFoundError(
            f"Hittade inte HDFS.log. Förväntad plats: {HDFS_LOG_PATH}"
        )

    SCENARIOS_DIR.mkdir(exist_ok=True)

    block_to_lines: dict[str, list[str]] = {
        block_id: []
        for _, block_id, _ in SCENARIOS
    }

    print(f"Läser HDFS.log från: {HDFS_LOG_PATH}")
    print("Extraherar loggrader för valda block-ID:n...\n")

    with HDFS_LOG_PATH.open("r", encoding="utf-8", errors="replace") as log_file:
        for line in log_file:
            line = line.rstrip("\n")

            for block_id in block_to_lines:
                if block_id in line:
                    block_to_lines[block_id].append(line)

    metadata_path = SCENARIOS_DIR / "metadata.csv"

    with metadata_path.open("w", newline="", encoding="utf-8") as metadata_file:
        writer = csv.writer(metadata_file)

        writer.writerow(
            [
                "scenario_id",
                "block_id",
                "label",
                "raw_file",
                "numbered_file",
                "line_count",
            ]
        )

        for scenario_id, block_id, label in SCENARIOS:
            matching_lines = block_to_lines[block_id]

            raw_text = "\n".join(matching_lines)
            numbered_text = number_log_lines(matching_lines)

            raw_filename = f"{scenario_id}_raw.txt"
            numbered_filename = f"{scenario_id}_numbered.txt"

            raw_path = SCENARIOS_DIR / raw_filename
            numbered_path = SCENARIOS_DIR / numbered_filename

            raw_path.write_text(raw_text, encoding="utf-8")
            numbered_path.write_text(numbered_text, encoding="utf-8")

            writer.writerow(
                [
                    scenario_id,
                    block_id,
                    label,
                    raw_filename,
                    numbered_filename,
                    len(matching_lines),
                ]
            )

            print(
                f"{scenario_id}: {block_id} ({label}) - "
                f"{len(matching_lines)} loggrader sparade"
            )

            if len(matching_lines) == 0:
                print(f"VARNING: Inga loggrader hittades för {block_id}")

    print(f"\nKlar. Scenarier sparade i: {SCENARIOS_DIR}")
    print(f"Metadata sparad i: {metadata_path}")


if __name__ == "__main__":
    main()