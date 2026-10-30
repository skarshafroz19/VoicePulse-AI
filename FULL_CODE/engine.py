"""
VoicePulse AI — Core Operational Engine (Saffron Retail Group / TalentAP Mega Hackathon 2026 - R5)
Turning Store Chatter into Action: Multilingual Ingestion, 33-Class Taxonomy Routing,
Policy-First Statutory Severities, Same-Day Deduplication, and Causal Emerging Incident Radar.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion

POLICY_HIGH_SEVERITY_ISSUES = {
    "IT04",  # Staff misconduct (abusive, harassment, cheating)
    "IT06",  # Hygiene lapse (pests, dirty food areas, foul smell)
    "IT08",  # Physical safety hazard (wet floor, wiring, falling stock)
    "IT10",  # Refrigeration / cold-chain failure
    "IT16",  # Expired / near-expiry product on shelf
    "IT17",  # Foreign object / contamination in product
    "IT18",  # Allergen / ingredient labelling error
}

POLICY_MEDIUM_SEVERITY_ISSUES = {
    "IT27",  # Payment failure / money debited but order failed
}

SEV_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}
REV_SEV_RANK = {0: "low", 1: "medium", 2: "high", 3: "critical"}


def extract_locality(store_name: str) -> str:
    """Extract store locality from name (e.g. 'Saffron Market Kothrud' -> 'Kothrud')."""
    if not isinstance(store_name, str):
        return ""
    clean = re.sub(r"Saffron (?:Hyper|Market|Express)\s*", "", store_name, flags=re.IGNORECASE).strip()
    return clean


def normalise_text(text: str) -> str:
    """Normalize whitespace and lowercase while preserving multilingual/code-mixed tokens."""
    if not isinstance(text, str):
        return ""
    t = text.lower().strip()
    t = re.sub(r"https?://\S+|www\.\S+", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t


def resolve_store_ids(
    df: pd.DataFrame,
    store_master: pd.DataFrame,
    store_col: str = "store_id",
    text_col: str = "text"
) -> pd.Series:
    """
    Resolve missing store_ids using locality matching from store_master.
    Locality matching is case-insensitive on word boundaries.
    """
    loc_to_store: dict[str, str] = {}
    for _, r in store_master.iterrows():
        loc = extract_locality(str(r.get("store_name", ""))).lower()
        if len(loc) >= 3:
            loc_to_store[loc] = str(r["store_id"])

    resolved: list[str | None] = []
    for s_val, txt_val in zip(df[store_col], df[text_col]):
        if pd.notna(s_val) and str(s_val).strip() and str(s_val).strip().lower() not in {"nan", "none"}:
            resolved.append(str(s_val).strip())
        else:
            txt_l = normalise_text(str(txt_val))
            matched = None
            for loc, s_id in loc_to_store.items():
                if re.search(r"\b" + re.escape(loc) + r"\b", txt_l):
                    matched = s_id
                    break
            resolved.append(matched)

    return pd.Series(resolved, index=df.index, dtype=object)


class VoicePulseClassifier:
    """
    Multilingual text classifier trained on official feedback_labels_train.csv.
    Uses a hybrid Word + Subword FeatureUnion with policy-first statutory floors.
    Predicts issue_type_id (33 classes), severity, and actionable flag.
    """

    def __init__(self) -> None:
        self.clf_issue = LogisticRegression(C=3.5, max_iter=1000, random_state=42)
        self.clf_sev = LogisticRegression(C=2.5, max_iter=1000, random_state=42)
        self.clf_act = LogisticRegression(C=2.5, max_iter=1000, random_state=42)
        self.vec: FeatureUnion | None = None
        self.is_fitted = False
        self.floor_map: dict[str, str] = {}

    def fit(self, train_df: pd.DataFrame, taxonomy_df: pd.DataFrame | None = None) -> VoicePulseClassifier:
        """Fit classifiers on labeled training data (feedback_id, issue_type_id, severity, actionable, text)."""
        texts = train_df["text"].map(normalise_text)
        word_min_df = 2 if len(train_df) > 50 else 1
        char_min_df = 3 if len(train_df) > 50 else 1
        self.vec = FeatureUnion([
            ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=word_min_df, sublinear_tf=True)),
            ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=char_min_df, sublinear_tf=True)),
        ])
        X = self.vec.fit_transform(texts)

        self.clf_issue.fit(X, train_df["issue_type_id"])
        self.clf_sev.fit(X, train_df["severity"])
        self.clf_act.fit(X, train_df["actionable"])

        if taxonomy_df is not None and "issue_type_id" in taxonomy_df.columns:
            self.floor_map = taxonomy_df.set_index("issue_type_id")["policy_severity_floor"].to_dict()

        self.is_fitted = True
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate issue_type_id, severity, and actionable for input records."""
        if not self.is_fitted:
            raise RuntimeError("Classifier must be fitted before predict.")

        texts = df["text"].map(normalise_text)
        X = self.vec.transform(texts)

        pred_issues = self.clf_issue.predict(X)
        pred_sevs = self.clf_sev.predict(X)
        pred_acts = self.clf_act.predict(X)

        # Apply statutory policy floor overrides: max(policy floor, impact)
        final_sevs: list[str] = []
        for iss, raw_s in zip(pred_issues, pred_sevs):
            floor = self.floor_map.get(iss, "low")
            if iss in POLICY_HIGH_SEVERITY_ISSUES:
                floor = "high"
            elif iss in POLICY_MEDIUM_SEVERITY_ISSUES:
                floor = "medium"

            raw_rank = SEV_RANK.get(raw_s, 0)
            floor_rank = SEV_RANK.get(floor, 0)
            final_sevs.append(REV_SEV_RANK[max(raw_rank, floor_rank)])

        # Non-actionable categories (NI01, NI02, NI03) must strictly have actionable = 0
        final_acts = pred_acts.copy()
        for idx, iss in enumerate(pred_issues):
            if iss in {"NI01", "NI02", "NI03"}:
                final_acts[idx] = 0

        res = df.copy()
        res["issue_type_id"] = pred_issues
        res["severity"] = final_sevs
        res["actionable"] = final_acts
        return res

    def predict_detailed(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate predictions with genuine probability confidence scores and statutory override audit details.
        """
        if not self.is_fitted:
            raise RuntimeError("Classifier must be fitted before predict.")

        texts = df["text"].map(normalise_text)
        X = self.vec.transform(texts)

        pred_issues = self.clf_issue.predict(X)
        pred_sevs = self.clf_sev.predict(X)
        pred_acts = self.clf_act.predict(X)

        proba_issues = self.clf_issue.predict_proba(X)
        proba_sevs = self.clf_sev.predict_proba(X)
        proba_acts = self.clf_act.predict_proba(X)

        issue_confs = np.max(proba_issues, axis=1)
        sev_confs = np.max(proba_sevs, axis=1)
        act_confs = np.max(proba_acts, axis=1)

        final_sevs: list[str] = []
        override_flags: list[bool] = []
        for iss, raw_s in zip(pred_issues, pred_sevs):
            floor = self.floor_map.get(iss, "low")
            if iss in POLICY_HIGH_SEVERITY_ISSUES:
                floor = "high"
            elif iss in POLICY_MEDIUM_SEVERITY_ISSUES:
                floor = "medium"

            raw_rank = SEV_RANK.get(raw_s, 0)
            floor_rank = SEV_RANK.get(floor, 0)
            chosen_sev = REV_SEV_RANK[max(raw_rank, floor_rank)]
            final_sevs.append(chosen_sev)
            override_flags.append(chosen_sev != raw_s)

        final_acts = pred_acts.copy()
        for idx, iss in enumerate(pred_issues):
            if iss in {"NI01", "NI02", "NI03"}:
                final_acts[idx] = 0

        res = df.copy()
        res["issue_type_id"] = pred_issues
        res["raw_severity"] = pred_sevs
        res["severity"] = final_sevs
        res["actionable"] = final_acts
        res["issue_confidence"] = issue_confs
        res["severity_confidence"] = sev_confs
        res["actionable_confidence"] = act_confs
        res["policy_override_applied"] = override_flags
        return res


def deduplicate_same_day(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect cross-channel duplicate complaints from the same store on the same calendar day
    sharing normalized text signatures.
    """
    d = df.copy()
    if "created_at" in d.columns:
        dt_parsed = pd.to_datetime(d["created_at"], errors="coerce")
        d["_day"] = dt_parsed.dt.date
    else:
        d["_day"] = "unknown"

    d["_norm_text"] = d["text"].astype(str).str.lower().str.replace(r"[^a-z0-9\s]", " ", regex=True).str.strip()
    s_col = "resolved_store_id" if "resolved_store_id" in d.columns else "store_id"
    d["_s_clean"] = d[s_col].fillna("UNASSIGNED")

    d["duplicate_group"] = d.groupby(["_s_clean", "_day", "_norm_text"]).ngroup().astype(str)
    d["is_duplicate"] = d.duplicated(subset=["_s_clean", "_day", "_norm_text"], keep="first")

    d.drop(columns=["_day", "_norm_text", "_s_clean"], inplace=True, errors="ignore")
    return d


def detect_emerging_incidents(
    feedback_df: pd.DataFrame,
    store_master_df: pd.DataFrame,
    as_of_week_start: str | None = None
) -> pd.DataFrame:
    """
    Causal weekly emerging-issue detector.
    Computes rolling 8-week baseline per (store, issue type), calculates z-scores,
    applies policy-first priority boosts, and selects at most 3 non-monopolized flags
    per week backed by valid contemporaneous evidence.
    """
    fb = feedback_df.copy()
    fb["dt"] = pd.to_datetime(fb["created_at"], errors="coerce")
    fb["week_start"] = fb["dt"].apply(
        lambda d: (d - pd.Timedelta(days=d.weekday())).strftime("%Y-%m-%d") if pd.notna(d) else "unknown"
    )

    if "resolved_store_id" not in fb.columns:
        fb["resolved_store_id"] = resolve_store_ids(fb, store_master_df)

    # Store operational issue types (IT01-IT22, IT30)
    store_issue_types = {f"IT{i:02d}" for i in range(1, 23)} | {"IT30"}
    fb_store = fb[fb["resolved_store_id"].notna() & fb["issue_type_id"].isin(store_issue_types)].copy()

    grouped = fb_store.groupby(["week_start", "resolved_store_id", "issue_type_id"]).agg(
        cnt=("feedback_id", "count"),
        ids=("feedback_id", lambda x: ";".join(list(x)))
    ).reset_index()

    all_weeks = sorted([w for w in fb["week_start"].unique() if w != "unknown"])
    target_weeks = [as_of_week_start] if as_of_week_start else all_weeks

    flags: list[dict[str, object]] = []

    for w in target_weeks:
        if w not in all_weeks:
            continue
        w_idx = all_weeks.index(w)
        hist_weeks = all_weeks[max(0, w_idx - 8):w_idx]
        if len(hist_weeks) < 2:
            continue

        hist_df = grouped[grouped["week_start"].isin(hist_weeks)]
        hist_stats = hist_df.groupby(["resolved_store_id", "issue_type_id"])["cnt"].agg(["mean", "std"]).reset_index()

        curr = grouped[grouped["week_start"] == w].merge(
            hist_stats, on=["resolved_store_id", "issue_type_id"], how="left"
        )
        curr["mean"] = curr["mean"].fillna(0.0)
        curr["std"] = curr["std"].fillna(0.5).clip(lower=0.5)
        curr["z"] = (curr["cnt"] - curr["mean"]) / curr["std"]

        curr["is_high_policy"] = curr["issue_type_id"].isin(POLICY_HIGH_SEVERITY_ISSUES)
        # Priority balance: z-score + policy hazard weight + volume
        curr["priority"] = curr["z"] + curr["is_high_policy"].astype(float) * 10.0 + curr["cnt"] * 0.5

        # Must have at least 2 evidence records per official Evidence Rule
        cands = curr[curr["cnt"] >= 2].sort_values("priority", ascending=False)

        seen_stores = set()
        picked = 0
        for _, r in cands.iterrows():
            st_id = r["resolved_store_id"]
            if st_id in seen_stores:
                continue
            flags.append({
                "as_of_week_start": w,
                "store_id": st_id,
                "issue_type_id": r["issue_type_id"],
                "confidence": round(float(np.clip(r["z"] / 5.0, 0.0, 1.0)), 2),
                "evidence_feedback_ids": r["ids"]
            })
            seen_stores.add(st_id)
            picked += 1
            if picked >= 3:
                break

    return pd.DataFrame(flags, columns=[
        "as_of_week_start", "store_id", "issue_type_id", "confidence", "evidence_feedback_ids"
    ])


def build_regional_weekly_brief(
    scored_df: pd.DataFrame,
    store_master: pd.DataFrame,
    taxonomy_df: pd.DataFrame,
    region: str,
    week_start: str,
    prev_week_start: str | None = None
) -> str:
    """
    Build a weekly one-page brief per region:
    top 5 issues, evidence quotes, affected stores, and a trend arrow vs last week.
    """
    tax_name_map = taxonomy_df.set_index("issue_type_id")["issue_type"].to_dict()
    tax_owner_map = taxonomy_df.set_index("issue_type_id")["owner_function"].to_dict()

    m = scored_df.merge(store_master[["store_id", "store_name", "region"]], on="store_id", how="left")
    curr_df = m[(m["region"] == region) & (m["week_start"] == week_start)]
    prev_df = m[(m["region"] == region) & (m["week_start"] == prev_week_start)] if prev_week_start else pd.DataFrame()

    total_records = len(curr_df)
    actionable_count = int(curr_df["actionable"].sum()) if "actionable" in curr_df.columns else 0
    high_critical = int(curr_df["severity"].isin(["high", "critical"]).sum()) if "severity" in curr_df.columns else 0

    prev_counts = prev_df["issue_type_id"].value_counts().to_dict() if not prev_df.empty else {}

    top_issues = curr_df[curr_df["issue_type_id"].str.startswith("IT")]["issue_type_id"].value_counts().head(5)

    brief_lines = [
        f"# Regional Weekly Action Brief: {region.upper()} REGION",
        f"**Week Commencing:** {week_start}  |  **Total Feedback:** {total_records:,}  |  **Actionable Tickets:** {actionable_count:,}  |  **High/Critical Safety:** {high_critical:,}",
        "",
        "## Top 5 Operational Issues & Function Routing",
        "",
        "| Rank | Issue Code & Description | Owning Function | Volume | Trend vs Last Week | Stores Affected | Sample Evidence Quote |",
        "| :--- | :--- | :--- | :--- | :---: | :--- | :--- |"
    ]

    for rank, (iss_id, cnt) in enumerate(top_issues.items(), 1):
        iss_name = tax_name_map.get(iss_id, iss_id)
        owner = tax_owner_map.get(iss_id, "Store Ops")
        p_cnt = prev_counts.get(iss_id, 0)

        if p_cnt == 0:
            trend = "NEW"
        elif cnt > p_cnt * 1.15:
            trend = "▲ RISING"
        elif cnt < p_cnt * 0.85:
            trend = "▼ FALLING"
        else:
            trend = "► STABLE"

        iss_records = curr_df[curr_df["issue_type_id"] == iss_id]
        stores_affected = ", ".join(iss_records["store_id"].dropna().unique()[:3])
        if not stores_affected:
            stores_affected = "Regional / App"

        sample_quote = iss_records["text"].dropna().iloc[0] if not iss_records.empty else "N/A"
        clean_quote = sample_quote.replace("\n", " ").replace("|", "/").strip()[:100] + "..."

        brief_lines.append(
            f"| {rank} | **{iss_id}**: {iss_name} | `{owner}` | **{cnt}** | {trend} | {stores_affected} | \"{clean_quote}\" |"
        )

    brief_lines.extend([
        "",
        "## Policy Escalation Rule Notice",
        "- All statutory compliance, life-safety, cold-chain refrigeration, and allergen issues (`IT04`, `IT06`, `IT08`, `IT10`, `IT16`, `IT17`, `IT18`) have policy severity floors at **HIGH** and trigger immediate store manager inspection.",
        "- Payment deduction failures (`IT27`) are enforced at **MEDIUM** floor and routed directly to Digital Product Ops."
    ])

    return "\n".join(brief_lines)
