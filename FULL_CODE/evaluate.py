import argparse
import os
import sys

# Ensure current and parent directories are in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
from engine import (
    deduplicate_records,
    emerging_incidents,
    evaluate_incident_lead_time,
    prepare_feedback,
    score_feedback,
)
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)

# Configure UTF-8 stdout for CLI
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def parse_args():
    p = argparse.ArgumentParser(description="VoicePulse AI Evaluation & Benchmarking Suite")
    p.add_argument("--input", required=True, help="Path to input feedback CSV (e.g. synthetic_validation_4000.csv or synthetic_feedback_40000.csv)")
    p.add_argument("--true-issue", default="issue_type_true", help="Ground truth column for issue type")
    p.add_argument("--true-severity", default="severity_true", help="Ground truth column for severity")
    p.add_argument("--true-actionable", default="actionable_true", help="Ground truth column for actionable")
    p.add_argument("--true-owner", default="owning_function_true", help="Ground truth column for owning function")
    p.add_argument("--store-master", default=None, help="Path to store master CSV")
    p.add_argument("--manifest", default=None, help="Path to synthetic incident manifest CSV")
    p.add_argument("--output-report", default=None, help="Optional output path to save Markdown report")
    p.add_argument("--eval-radar", action="store_true", default=True, help="Evaluate emerging incident radar and lead times")
    return p.parse_args()


def run_evaluation(args):
    print("=" * 80)
    print("📡 VoicePulse AI — Evaluation & Performance Report")
    print("AI Frontier Challenge 2026 — Problem R5")
    print("=" * 80)
    print("⚠️  IMPORTANT DISCLAIMER:")
    print("All metrics below are computed on the synthetic validation dataset.")
    print("These synthetic results are strictly separated from official hackathon benchmark results.")
    print("=" * 80)

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)

    print(f"\n[1/5] Ingesting feedback from '{args.input}'...")
    raw = pd.read_csv(args.input)
    print(f"Loaded {len(raw):,} raw feedback records.")

    # Store master resolution
    store_master_df = None
    if args.store_master and os.path.exists(args.store_master):
        store_master_df = pd.read_csv(args.store_master)
    else:
        candidates = [
            "synthetic_store_master.csv",
            os.path.join("..", "data", "synthetic_store_master.csv"),
            os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_store_master.csv")
        ]
        for c in candidates:
            if os.path.exists(c):
                store_master_df = pd.read_csv(c)
                break

    print("[2/5] Preparing and normalizing feedback schema...")
    prepared = prepare_feedback(raw, store_master=store_master_df)

    print("[3/5] Scoring feedback and applying policy overrides...")
    scored = score_feedback(prepared)

    print("[4/5] Running conservative deduplication...")
    deduped = deduplicate_records(scored)
    dup_count = int(deduped["is_duplicate"].sum())
    dup_groups = deduped["duplicate_group"].nunique()
    print(f"Identified {dup_count:,} duplicate records across {dup_groups:,} unique groups.")

    report_lines = [
        "# VoicePulse AI — Synthetic Evaluation Report",
        "",
        "> [!IMPORTANT]",
        "> **Synthetic Data Notice:** These metrics are generated on local synthetic validation data",
        "> (`synthetic_validation_4000.csv` / `synthetic_feedback_40000.csv`) and are maintained strictly separate",
        "> from official hackathon benchmark evaluations. No synthetic labels were used for test leakage.",
        "",
        f"- **Input Dataset:** `{args.input}` ({len(raw):,} records)",
        f"- **Stores Represented:** {prepared['store_id'].nunique():,}",
        f"- **Conservative Near-Duplicates:** {dup_count:,} records flagged",
        ""
    ]

    # Evaluate Classification Tasks
    print("\n[5/5] Evaluating predictions against ground-truth labels...")
    targets = [
        (args.true_issue, "issue_type", "Issue Type Classification"),
        (args.true_severity, "severity", "Severity Classification"),
        (args.true_actionable, "actionable", "Actionability Classification"),
        (args.true_owner, "owner", "Owning Function Routing")
    ]

    metrics_summary = {}

    for true_col, pred_col, task_name in targets:
        if true_col in raw.columns:
            y_true = raw[true_col].fillna("None").astype(str)
            y_pred = deduped[pred_col].fillna("None").astype(str)

            acc = accuracy_score(y_true, y_pred)
            macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
            weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

            print(f"\n{'='*30} {task_name} {'='*30}")
            print(f"Accuracy:    {acc:.4f} ({acc*100:.2f}%)")
            print(f"Macro F1:    {macro_f1:.4f}")
            print(f"Weighted F1: {weighted_f1:.4f}")
            print("\nDetailed Classification Report:")
            clf_rep = classification_report(y_true, y_pred, zero_division=0)
            print(clf_rep)

            metrics_summary[pred_col] = {
                "accuracy": round(acc, 4),
                "macro_f1": round(macro_f1, 4),
                "weighted_f1": round(weighted_f1, 4)
            }

            report_lines.extend([
                f"### {task_name}",
                f"- **Accuracy:** {acc*100:.2f}%",
                f"- **Macro F1:** {macro_f1:.4f}",
                f"- **Weighted F1:** {weighted_f1:.4f}",
                "",
                "```",
                clf_rep,
                "```",
                ""
            ])

            if pred_col == "severity":
                high_true = (y_true == "HIGH")
                high_pred = (y_pred == "HIGH")
                high_recall = recall_score(high_true, high_pred, zero_division=0)
                high_prec = precision_score(high_true, high_pred, zero_division=0)
                print(f"High-Severity Policy Recall:    {high_recall:.4f} ({high_recall*100:.2f}%)")
                print(f"High-Severity Policy Precision: {high_prec:.4f} ({high_prec*100:.2f}%)")
                report_lines.extend([
                    f"- **High-Severity Policy Recall:** {high_recall*100:.2f}%",
                    f"- **High-Severity Policy Precision:** {high_prec*100:.2f}%",
                    ""
                ])
        else:
            print(f"Note: Column '{true_col}' not present; skipping {task_name} evaluation.")

    # Emerging Incident Radar & Lead Time Evaluation
    radar_df = pd.DataFrame()
    if args.eval_radar:
        print("\n" + "=" * 30 + " Emerging Incident Radar & Lead Time " + "=" * 30)
        radar_df = emerging_incidents(deduped)
        print(f"Emerging Incident Radar generated {len(radar_df):,} alerts across timeline.")

        manifest_file = args.manifest
        if not manifest_file or not os.path.exists(manifest_file):
            candidate_manifests = [
                "synthetic_incident_manifest.csv",
                os.path.join("..", "data", "synthetic_incident_manifest.csv"),
                os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_incident_manifest.csv")
            ]
            for m in candidate_manifests:
                if os.path.exists(m):
                    manifest_file = m
                    break

        if manifest_file and os.path.exists(manifest_file):
            print(f"Evaluating radar lead times against manifest: '{manifest_file}'")
            manifest_df = pd.read_csv(manifest_file)
            lead_time_df = evaluate_incident_lead_time(radar_df, manifest_df, deduped)

            print("\nIncident Detection & Lead Time Summary:")
            print(lead_time_df[["incident_id", "store_id", "issue_type", "start_day", "detected_week", "alert_level", "surge_ratio", "detection_delay_days", "lead_time_vs_monthly_days", "status"]].to_string(index=False))

            report_lines.extend([
                "### Seeded Synthetic Incident Detection & Lead Time",
                "Comparison against standard 30-day monthly batch review baseline:",
                "",
                "| Incident ID | Store | Issue Type | Start Day | Detected Week | Alert Level | Surge Ratio | Delay (Days) | Lead Time Advantage | Status |",
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
            ])
            for _, r in lead_time_df.iterrows():
                report_lines.append(
                    f"| {r['incident_id']} | {r['store_id']} | {r['issue_type']} | {r['start_day']} | "
                    f"{r['detected_week']} | {r['alert_level']} | {r['surge_ratio']}x | "
                    f"{r['detection_delay_days']:+.1f} | +{r['lead_time_vs_monthly_days']:.1f} days | **{r['status']}** |"
                )
            report_lines.append("")
        else:
            print("Note: Incident manifest not found; skipping lead-time verification.")

    if args.output_report:
        with open(args.output_report, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        print(f"\nSuccessfully wrote detailed evaluation report to: {args.output_report}")

    print("\nEvaluation completed successfully.")
    return metrics_summary


if __name__ == "__main__":
    args = parse_args()
    run_evaluation(args)
