#!/usr/bin/env python3
"""
Generate a verification workbook from the current vs backup dataset.

Outputs:
  - audit/verification_fields.csv
  - audit/verification_items.csv
  - audit/verification_summary.md
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import math

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "data" / "csv" / "master_dataset.csv"
BACKUP = ROOT / "data" / "csv" / "master_dataset_backup.csv"
AUDIT_DIR = ROOT / "audit"

FIELD_OUTPUT = AUDIT_DIR / "verification_fields.csv"
ITEM_OUTPUT = AUDIT_DIR / "verification_items.csv"
SUMMARY_OUTPUT = AUDIT_DIR / "verification_summary.md"


FIELD_PRIORITY = {
    "URL": "Critical",
    "Title_Caption": "Critical",
    "Creator_Name": "Critical",
    "Creator_Type": "Critical",
    "Date_Posted": "Critical",
    "Views": "High",
    "Likes": "High",
    "Comments": "High",
    "Shares": "High",
    "Content_Format": "High",
    "Creator_Credentials": "High",
    "Notes": "Medium",
}

PRIORITY_ORDER = {"Critical": 3, "High": 2, "Medium": 1, "Low": 0}

RAW_SOURCE_BY_PLATFORM = {
    "Website": "data/csv/google_results.csv",
    "YouTube": "data/csv/youtube_results.csv",
    "TikTok": "data/csv/tiktok_results.csv",
    "Instagram": "data/csv/instagram_results.csv",
}

SCREENSHOT_DIR_BY_PREFIX = {
    "WEB": "data/screenshots/google",
    "YT": "data/screenshots/youtube",
    "TT": "data/screenshots/tiktok",
    "IG": "data/screenshots/instagram",
}


def normalize(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    text = str(value)
    return "" if text == "nan" else text


def looks_like_number(text: str) -> bool:
    if not text:
        return False
    try:
        float(text)
        return True
    except ValueError:
        return False


def looks_like_date(text: str) -> bool:
    if not text:
        return False
    try:
        pd.Timestamp(text)
        return True
    except (ValueError, TypeError):
        return False


def screenshot_path(item_id: str) -> str:
    prefix = item_id.split("-")[0]
    folder = SCREENSHOT_DIR_BY_PREFIX.get(prefix)
    if not folder:
        return ""
    return str(Path(folder) / f"{item_id}.png")


def field_reason(field: str, old: str, new: str) -> str:
    if field == "URL":
        return "Replacement content item or source URL swap."
    if field == "Creator_Type":
        return "Manual creator-type reassignment can change inferential results."
    if field == "Date_Posted":
        if not looks_like_date(old) and looks_like_date(new):
            return "Date appears to have been generated or reconstructed."
        return "Date change affects inclusion criteria and recency claims."
    if field in {"Views", "Likes", "Comments", "Shares"}:
        if not old and new:
            return "Metric appears to have been filled where missing."
        return "Metric change affects engagement analyses."
    if field == "Content_Format":
        if looks_like_number(old) or not old:
            return "Format likely repaired after a column shift or recoding."
        return "Format change affects descriptive and exploratory analyses."
    if field in {"Creator_Name", "Creator_Credentials", "Title_Caption"}:
        return "Metadata repair likely requires screenshot or raw export verification."
    if field == "Notes":
        return "Narrative note changed; low statistical impact but may affect interpretation."
    return "Metadata changed and should be verified against primary evidence."


def likely_source(field: str, platform: str, item_id: str) -> str:
    if field in {"URL", "Title_Caption", "Creator_Name", "Creator_Credentials", "Date_Posted", "Views", "Likes", "Comments", "Shares"}:
        return f"{RAW_SOURCE_BY_PLATFORM.get(platform, '')}; {screenshot_path(item_id)}"
    if field in {"Creator_Type", "Content_Format"}:
        return f"{screenshot_path(item_id)}; scoring spreadsheet/codebook"
    return screenshot_path(item_id)


def thesis_impact(field: str) -> str:
    if field in {"URL", "Date_Posted"}:
        return "Affects sample validity and inclusion criteria."
    if field in {"Creator_Type"}:
        return "Affects RQ2 creator-type results."
    if field in {"Views", "Likes", "Comments", "Shares"}:
        return "Affects RQ3 engagement results."
    if field in {"Content_Format"}:
        return "Affects exploratory format analysis and descriptive tables."
    if field in {"Title_Caption", "Creator_Name", "Creator_Credentials"}:
        return "Affects descriptive accuracy and possibly coding decisions."
    return "Low direct statistical impact; verify for transparency."


def item_priority(changed_fields: list[str], item_id: str) -> str:
    highest = max(PRIORITY_ORDER[FIELD_PRIORITY.get(field, "Low")] for field in changed_fields)
    if len(changed_fields) >= 5:
        highest = max(highest, PRIORITY_ORDER["Critical"])
    if "URL" in changed_fields:
        highest = PRIORITY_ORDER["Critical"]
    inverse = {v: k for k, v in PRIORITY_ORDER.items()}
    return inverse[highest]


def main() -> None:
    AUDIT_DIR.mkdir(exist_ok=True)

    current = pd.read_csv(CURRENT)
    backup = pd.read_csv(BACKUP)

    backup_by_id = backup.set_index("Item_ID")

    field_rows: list[dict[str, str]] = []
    item_changes: dict[str, list[str]] = defaultdict(list)
    item_meta: dict[str, dict[str, str]] = {}

    shared_cols = [c for c in current.columns if c in backup.columns and c != "Item_ID"]

    for _, row in current.iterrows():
        item_id = row["Item_ID"]
        if item_id not in backup_by_id.index:
            continue
        old_row = backup_by_id.loc[item_id]
        platform = normalize(row["Platform"])
        search_term = normalize(row.get("Search_Term", ""))

        for field in shared_cols:
            old = normalize(old_row[field])
            new = normalize(row[field])
            if old == new:
                continue

            priority = FIELD_PRIORITY.get(field, "Low")
            field_rows.append(
                {
                    "item_id": item_id,
                    "platform": platform,
                    "search_term": search_term,
                    "field": field,
                    "priority": priority,
                    "old_value": old,
                    "current_value": new,
                    "reason_to_verify": field_reason(field, old, new),
                    "thesis_impact": thesis_impact(field),
                    "raw_source_csv": RAW_SOURCE_BY_PLATFORM.get(platform, ""),
                    "screenshot_path": screenshot_path(item_id),
                    "likely_verification_source": likely_source(field, platform, item_id),
                    "verification_status": "",
                    "verified_value": "",
                    "verifier_notes": "",
                }
            )
            item_changes[item_id].append(field)
            item_meta[item_id] = {
                "platform": platform,
                "search_term": search_term,
                "raw_source_csv": RAW_SOURCE_BY_PLATFORM.get(platform, ""),
                "screenshot_path": screenshot_path(item_id),
            }

    field_df = pd.DataFrame(field_rows)
    if not field_df.empty:
        field_df["priority_rank"] = field_df["priority"].map(PRIORITY_ORDER)
        field_df = field_df.sort_values(
            ["priority_rank", "item_id", "field"],
            ascending=[False, True, True],
        ).drop(columns=["priority_rank"])
    field_df.to_csv(FIELD_OUTPUT, index=False, encoding="utf-8-sig")

    item_rows = []
    for item_id, fields in item_changes.items():
        meta = item_meta[item_id]
        uniq_fields = sorted(set(fields))
        priority = item_priority(uniq_fields, item_id)
        item_rows.append(
            {
                "item_id": item_id,
                "platform": meta["platform"],
                "search_term": meta["search_term"],
                "priority": priority,
                "changed_field_count": len(uniq_fields),
                "changed_fields": ", ".join(uniq_fields),
                "raw_source_csv": meta["raw_source_csv"],
                "screenshot_path": meta["screenshot_path"],
                "verification_status": "",
                "item_notes": "",
            }
        )

    item_df = pd.DataFrame(item_rows)
    if not item_df.empty:
        item_df["priority_rank"] = item_df["priority"].map(PRIORITY_ORDER)
        item_df = item_df.sort_values(
            ["priority_rank", "changed_field_count", "item_id"],
            ascending=[False, False, True],
        ).drop(columns=["priority_rank"])
    item_df.to_csv(ITEM_OUTPUT, index=False, encoding="utf-8-sig")

    field_counts = Counter(field_df["field"]) if not field_df.empty else Counter()
    priority_counts = Counter(item_df["priority"]) if not item_df.empty else Counter()

    with SUMMARY_OUTPUT.open("w", encoding="utf-8") as fh:
        fh.write("# Verification Summary\n\n")
        fh.write(f"- Changed items: {len(item_df)}\n")
        fh.write(f"- Changed fields: {len(field_df)}\n\n")

        fh.write("## Item Priority Counts\n\n")
        for priority in ["Critical", "High", "Medium", "Low"]:
            if priority in priority_counts:
                fh.write(f"- {priority}: {priority_counts[priority]}\n")
        fh.write("\n## Most Changed Fields\n\n")
        for field, count in field_counts.most_common():
            fh.write(f"- `{field}`: {count}\n")

        fh.write("\n## First Items To Verify\n\n")
        for _, row in item_df.head(20).iterrows():
            fh.write(
                f"- `{row['item_id']}` ({row['platform']}): {row['changed_field_count']} fields changed; "
                f"{row['changed_fields']}\n"
            )

        fh.write("\n## How To Use\n\n")
        fh.write("- Verify `Critical` items first against raw CSV exports and screenshots.\n")
        fh.write("- Enter verification decisions directly into `verification_fields.csv` or `verification_items.csv`.\n")
        fh.write("- Do not rerun the thesis analysis until all `Critical` fields are either verified, reverted, or dropped.\n")

    print(f"Wrote {FIELD_OUTPUT}")
    print(f"Wrote {ITEM_OUTPUT}")
    print(f"Wrote {SUMMARY_OUTPUT}")


if __name__ == "__main__":
    main()
