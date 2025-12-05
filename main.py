from syftbox.lib import Client
from pathlib import Path
from collections import Counter
import json


def main() -> None:
    # Load SyftBox client (provided automatically inside the App environment)
    client = Client.load()

    # ------------------------------------------------------------------
    # 1. Locate the dataset on the OWNER's datasite
    # ------------------------------------------------------------------
    # This assumes the StarCraft dataset lives at:
    #
    #   <datasite-root>/semi-public/team-project/data/
    #
    # i.e. matching your dataset.yaml path:
    #   ~/Downloads/OPENMINED/SyftBox/datasites/kj@psistorm.com/semi-public/team-project
    #
    # If you move the dataset, just adjust this one line:
    dataset_root = client.my_datasite / "semi-public" / "team-project" / "data"

    patterns_path = dataset_root / "patterns.json"

    # ------------------------------------------------------------------
    # 2. Load patterns.json (structure you described above)
    # ------------------------------------------------------------------
    with patterns_path.open("r", encoding="utf-8") as f:
        patterns_obj = json.load(f)

    # patterns_obj structure:
    # {
    #   "pattern_001": PatternEntry,
    #   "pattern_002": PatternEntry,
    #   ...
    # }

    total_patterns = len(patterns_obj)

    # ------------------------------------------------------------------
    # 3. Filter for Protoss builds
    # ------------------------------------------------------------------
    protoss_patterns = {}
    for pattern_id, entry in patterns_obj.items():
        race = (entry.get("race") or "").lower()
        if race == "protoss":
            protoss_patterns[pattern_id] = entry

    protoss_count = len(protoss_patterns)

    # Basic breakdown by strategy_type
    strategy_counts = Counter(
        (entry.get("strategy_type") or "unknown")
        for entry in protoss_patterns.values()
    )

    # ------------------------------------------------------------------
    # 4. Build a compact, review-friendly summary
    # ------------------------------------------------------------------
    example_entries = []

    # Take up to 10 example Protoss patterns
    for pattern_id, entry in list(protoss_patterns.items())[:10]:
        sig = entry.get("signature", {})
        opening_seq = sig.get("opening_sequence", []) or []

        # Just capture the unit names for readability
        opening_units = [step.get("unit") for step in opening_seq]

        example_entries.append(
            {
                "pattern_id": pattern_id,
                "race": entry.get("race"),
                "strategy_type": entry.get("strategy_type"),
                "sample_count": entry.get("sample_count"),
                "confidence": entry.get("confidence"),
                "opening_sequence_units": opening_units,
            }
        )

    result = {
        "total_patterns": total_patterns,
        "protoss_pattern_count": protoss_count,
        "protoss_strategy_breakdown": dict(strategy_counts),
        "example_protoss_patterns": example_entries,
    }

    # ------------------------------------------------------------------
    # 5. Write result into the owner's PUBLIC folder
    # ------------------------------------------------------------------
    output_path = client.my_datasite / "public" / "starcraft_protoss_summary.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"[SyftBox App] Wrote Protoss summary to: {output_path}")


if __name__ == "__main__":
    main()

