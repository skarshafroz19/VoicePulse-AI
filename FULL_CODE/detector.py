#!/usr/bin/env python3
"""
VoicePulse AI — Causal Weekly Emerging Issue Detector CLI
Interface compatible with TalentAP Mega Hackathon 2026 R5 evaluation:
    python FULL_CODE/detector.py --feedback {feedback} --as-of {asof} --out {out}

Reads feedback.csv, feedback_labels_train.csv, issue_taxonomy.csv, store_master.csv
from the folder containing --feedback. Uses only feedback up to that week's Sunday.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

# Add FULL_CODE directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import VoicePulseClassifier, detect_emerging_incidents, resolve_store_ids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VoicePulse AI Causal Emerging Incident Detector")
    parser.add_argument("--feedback", required=True, help="Path to feedback.csv")
    parser.add_argument("--as-of", dest="asof", required=True, help="Target week date (YYYY-MM-DD)")
    parser.add_argument("--out", required=True, help="Output path for flags CSV")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    feedback_path = Path(args.feedback).resolve()
    data_dir = feedback_path.parent

    labels_path = data_dir / "feedback_labels_train.csv"
    taxonomy_path = data_dir / "issue_taxonomy.csv"
    stores_path = data_dir / "store_master.csv"

    if not feedback_path.exists():
        sys.exit(f"Error: feedback file not found at {feedback_path}")

    print(f"Loading data from {data_dir}...")
    fb = pd.read_csv(feedback_path)
    labels = pd.read_csv(labels_path) if labels_path.exists() else pd.DataFrame()
    taxonomy = pd.read_csv(taxonomy_path) if taxonomy_path.exists() else pd.DataFrame()
    stores = pd.read_csv(stores_path) if stores_path.exists() else pd.DataFrame()

    # Determine week boundaries for --as-of
    asof_date = pd.to_datetime(args.asof).date()
    monday_date = asof_date - pd.Timedelta(days=asof_date.weekday())
    sunday_cutoff = monday_date + pd.Timedelta(days=6)
    monday_str = monday_date.strftime("%Y-%m-%d")

    # Strictly filter rows up to Sunday 23:59:59 (no future data)
    fb["dt"] = pd.to_datetime(fb["created_at"], errors="coerce")
    fb_causal = fb[fb["dt"].dt.date <= sunday_cutoff].copy()

    # Train classifier on available labels
    print("Training classifier on public ground truth...")
    train_m = labels.merge(fb[["feedback_id", "text"]], on="feedback_id")
    clf = VoicePulseClassifier().fit(train_m, taxonomy)

    # Predict classifications for causal feedback
    print("Classifying feedback records...")
    fb_causal = clf.predict(fb_causal)

    # Resolve store localities
    if not stores.empty:
        fb_causal["resolved_store_id"] = resolve_store_ids(fb_causal, stores)

    # Detect emerging flags for the target week
    print(f"Detecting emerging incidents for week {monday_str}...")
    flags_df = detect_emerging_incidents(fb_causal, stores, as_of_week_start=monday_str)

    # Write output flags
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    flags_df.to_csv(out_path, index=False)
    print(f"Wrote {len(flags_df)} flags for week {monday_str} to {out_path}")


if __name__ == "__main__":
    main()
