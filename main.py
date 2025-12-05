"""
This SyftBox app reads a private StarCraft II dataset and produces a
privacy-safe summary about Protoss strategy patterns. It does NOT
expose any raw game data — only counts and aggregated statistics.

This file is executed INSIDE the datasite owner's machine when SyftBox
runs the app. The requesting user NEVER sees raw data; only the public
summary file.

All filesystem paths are computed dynamically based on where SyftBox
installs the app, so no absolute paths are required.
"""

from pathlib import Path
from collections import Counter
import json

# ================================================================
# CONFIGURATION SECTION
# ================================================================

# The email of the datasite owner whose data we are analyzing.
# This matches the folder name inside:
#   SyftBox/datasites/<OWNER_EMAIL>/
OWNER_EMAIL = "kj@psistorm.com"

# The relative path (inside the datasite) where the dataset files live.
# In this case, the dataset is located at:
#   SyftBox/datasites/kj@psistorm.com/semi-public/team-project/
#
# So we define that path relative to the datasite root:
DATASET_REL_PATH = Path("semi-public") / "team-project"

# The location where we will write the final public summary file.
# This ends up at:
#   SyftBox/datasites/kj@psistorm.com/public/protoss_summary.json
OUTPUT_FILE = Path("public") / "protoss_summary.json"


# ================================================================
# MAIN APPLICATION LOGIC
# ================================================================

def main() -> None:
    """
    Main entry point for the app.
    This function:
      - Locates the SyftBox installation and datasite folders
      - Loads the patterns.json dataset file
      - Filters Protoss patterns
      - Computes privacy-safe summary statistics
      - Writes a public JSON summary file
    """

    # ----------------------------------------------------------------
    # 1. Figure out where SyftBox installed this app.
    # ----------------------------------------------------------------
    # __file__  gives the path to THIS script.
    # parent    gives its directory.
    app_dir = Path(__file__).resolve().parent

    # SyftBox installs apps like this:
    #   SyftBox/apps/<app-id>/main.py
    #
    # So:
    #   main.py                 -> parent (app_dir)
    #   app folder              -> app_dir
    #   apps/ (folder)          -> app_dir.parent
    #   SyftBox root folder     -> app_dir.parent.parent
    syftbox_root = app_dir.parent.parent

    # ----------------------------------------------------------------
    # 2. Build the path to the datasite owner's root folder.
    # ----------------------------------------------------------------
    # Datasites live under:
    #   SyftBox/datasites/<owner-email>/
    datasite_root = syftbox_root / "datasites" / OWNER_EMAIL

    # ----------------------------------------------------------------
    # 3. Build the path to the dataset inside that datasite.
    # ----------------------------------------------------------------
    dataset_root = datasite_root / DATASET_REL_PATH

    # The dataset includes these files:
    #   patterns.json
    #   comments.json
    #   learning_stats.json
    # We only need patterns.json for this app.
    patterns_path = dataset_root / "patterns.json"

    # Check whether patterns.json actually exists.
    # If not, fail early with a clear error message.
    if not patterns_path.exists():
        raise FileNotFoundError(
            f"patterns.json not found at: {patterns_path}\n"
            "Ensure the dataset files are in the expected SyftBox datasite folder."
        )

    # ----------------------------------------------------------------
    # 4. Load patterns.json into memory.
    # ----------------------------------------------------------------
    # patterns.json is a dictionary mapping pattern IDs (like "pattern_001")
    # to pattern data structures that include:
    #   - race
    #   - strategy_type
    #   - signature (build-order info)
    #   - sample_count
    #   - confidence
    #   - etc.
    with patterns_path.open("r", encoding="utf-8") as f:
        patterns = json.load(f)

    # ----------------------------------------------------------------
    # 5. Filter to ONLY Protoss patterns.
    # ----------------------------------------------------------------
    # We check each entry's "race" field and compare it case-insensitively.
    protoss_patterns = {
        pattern_id: entry
        for pattern_id, entry in patterns.items()
        if (entry.get("race") or "").lower() == "protoss"
    }

    # ----------------------------------------------------------------
    # 6. Count how many Protoss strategies fall into each strategy type.
    # ----------------------------------------------------------------
    # The "strategy_type" field is safe to share because it's a general
    # category like "protoss_aggression" or "economic_expansion".
    strategy_breakdown = Counter(
        (entry.get("strategy_type") or "unknown")
        for entry in protoss_patterns.values()
    )

    # ----------------------------------------------------------------
    # 7. Prepare a privacy-safe summary.
    # ----------------------------------------------------------------
    # We DO NOT include:
    #   - individual build steps
    #   - pattern IDs
    #   - comments
    #   - timestamps
    #   - opponent information
    #   - raw gameplay data
    #
    # Only aggregate counts are returned.
    result = {
        "total_patterns_in_dataset": len(patterns),
        "protoss_pattern_count": len(protoss_patterns),
        "protoss_strategy_breakdown": dict(strategy_breakdown),
    }

    # ----------------------------------------------------------------
    # 8. Write summary to the public folder.
    # ----------------------------------------------------------------
    # This allows the requesting user (karl) to read the output safely.
    output_path = datasite_root / OUTPUT_FILE

    # Ensure the public folder exists.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write JSON output.
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    # Helpful log output for debugging.
    print(f"[App] Privacy-safe summary written to: {output_path}")


# ================================================================
# SCRIPT ENTRY POINT
# ================================================================

# This ensures the app only executes when SyftBox runs it directly.
if __name__ == "__main__":
    main()

