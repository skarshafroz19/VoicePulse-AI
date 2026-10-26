import hashlib
import os
import re

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------
# Default 31-Class Operational Taxonomy & Owning Functions
# ---------------------------------------------------------
DEFAULT_TAXONOMY = {
    "freezer_cold_chain": ("Supply Chain", [
        "freezer not cooling", "fridge is warm", "ice cream melted",
        "cold storage broken", "dairy section temperature high",
        "freezer broken", "fridge warm", "temperature high in dairy", "freezer failure"
    ]),
    "allergen_mislabel": ("Store Ops", [
        "allergen label is wrong", "contains peanut but label says no nuts",
        "gluten warning missing", "allergy information incorrect",
        "mislabelled allergen on packet", "allergen label wrong", "peanut allergy"
    ]),
    "hygiene_pest": ("Store Ops", [
        "cockroach near shelf", "store floor is dirty", "pest seen near food",
        "bad smell in storage", "hygiene issue at counter", "cockroach", "rat",
        "pest seen", "dirty floor", "hygiene issue"
    ]),
    "staff_misconduct": ("HR", [
        "staff member was rude", "cashier shouted at customer",
        "employee behaved abusively", "staff ignored complaint",
        "misconduct by store staff", "rude staff", "abusive staff", "staff shouted"
    ]),
    "billing_error": ("Store Ops", [
        "charged twice at billing", "billing counter error", "wrong amount on bill",
        "cashier scanned item twice", "payment deducted but bill failed",
        "wrong bill", "double charged", "billing error"
    ]),
    "long_queue": ("Store Ops", [
        "long queue at checkout", "billing line too slow", "waiting 25 minutes to pay",
        "queue not moving", "too few billing counters open", "long queue", "slow line"
    ]),
    "stockout": ("Supply Chain", [
        "item out of stock", "shelf empty again", "delivery not received",
        "popular product unavailable", "stock missing in aisle", "out of stock", "empty shelf"
    ]),
    "pricing_mismatch": ("Merchandising", [
        "shelf price differs from bill", "wrong price tag", "discount missing at checkout",
        "price label incorrect", "offer not applied", "price mismatch", "wrong price"
    ]),
    "app_crash": ("Digital", [
        "app keeps crashing", "app crash during checkout", "mobile app freezes",
        "app closes after login", "app not opening", "app crash", "mobile app crash"
    ]),
    "payment_failure": ("Digital", [
        "online payment failed", "payment deducted but order failed",
        "upi checkout error", "card payment not going through", "digital payment stuck",
        "payment failure", "upi payment failed"
    ]),
    "login_otp": ("Digital", [
        "otp not arriving", "cannot log in to app", "login keeps failing",
        "account access issue", "verification code expired", "otp issue", "login failure"
    ]),
    "delivery_delay": ("Supply Chain", [
        "delivery delayed again", "supplier delivery arrived late",
        "goods not delivered on time", "late replenishment", "delivery missed schedule",
        "delivery delay", "late delivery"
    ]),
    "damaged_goods": ("Supply Chain", [
        "product arrived damaged", "broken packaging on shelf",
        "items crushed in delivery", "damaged carton received", "leaking product pack",
        "damaged product", "crushed items"
    ]),
    "expired_goods": ("Store Ops", [
        "expired product on shelf", "best before date passed", "stale product sold",
        "outdated goods found", "expired item in refrigerator", "expired goods", "stale product"
    ]),
    "store_temperature": ("Store Ops", [
        "store is too hot", "air conditioning not working", "temperature uncomfortable",
        "ac broken near checkout", "store ventilation poor", "store too hot", "ac broken"
    ]),
    "lighting_electrical": ("Store Ops", [
        "lights flickering", "power socket sparking", "aisle lights not working",
        "electrical issue in store", "dark section near shelves", "sparking socket", "lights broken"
    ]),
    "equipment_breakdown": ("Store Ops", [
        "weighing scale broken", "scanner not working", "checkout machine stopped",
        "equipment keeps failing", "conveyor belt broken", "scale broken", "machine broken"
    ]),
    "staff_shortage": ("HR", [
        "not enough staff today", "only one cashier working", "understaffed shift",
        "no employee available to help", "staff shortage on floor", "understaffed", "shortage of staff"
    ]),
    "staff_training": ("HR", [
        "staff could not explain return policy", "employee gave wrong information",
        "cashier not trained on system", "staff unsure about product",
        "training gap at service desk", "untrained staff", "staff not trained"
    ]),
    "returns_refunds": ("Store Ops", [
        "refund still pending", "return rejected without reason", "refund process too slow",
        "return desk unavailable", "exchange request not handled", "refund pending", "return rejected"
    ]),
    "parking_access": ("Store Ops", [
        "parking area blocked", "no accessible parking", "parking signs confusing",
        "entry ramp obstructed", "parking lights broken", "parking blocked", "parking issue"
    ]),
    "shelf_restocking": ("Merchandising", [
        "shelves not restocked", "products left in back room", "empty display shelf",
        "items not arranged properly", "shelf replenishment delayed", "shelf restocking", "empty display"
    ]),
    "product_quality": ("Supply Chain", [
        "fruit quality poor", "vegetables spoiled", "product tastes unusual",
        "packaging seal broken", "quality issue with product", "poor quality", "spoiled fruit"
    ]),
    "customer_service": ("Store Ops", [
        "nobody helped me", "service desk ignored us", "staff did not answer question",
        "complaint not acknowledged", "poor customer support", "nobody helped", "service desk ignored"
    ]),
    "queue_management": ("Store Ops", [
        "express lane closed", "queue barriers confusing", "self checkout queue too long",
        "checkout line blocks aisle", "queue management poor", "express lane", "queue barriers"
    ]),
    "online_order": ("Digital", [
        "online order status stuck", "order missing from app", "wrong item in online order",
        "click and collect not ready", "order confirmation missing", "order status stuck", "click and collect"
    ]),
    "data_privacy": ("Digital", [
        "app showed another account details", "privacy concern with account",
        "personal details visible on screen", "unexpected account data shown",
        "data access concern", "privacy breach", "account data shown"
    ]),
    "workplace_safety": ("HR", [
        "spill caused slip hazard", "staff safety concern in stockroom",
        "blocked emergency exit", "unsafe ladder in back area", "workplace hazard not fixed",
        "slip hazard", "unsafe ladder", "emergency exit blocked", "safety hazard"
    ]),
    "waste_disposal": ("Store Ops", [
        "waste bin overflowing", "food waste not cleared", "recycling bins mixed up",
        "garbage smell behind store", "waste area dirty", "overflowing bin", "garbage smell"
    ]),
    "promotion_confusion": ("Merchandising", [
        "promotion terms unclear", "buy one get one not applied",
        "offer sign still displayed after expiry", "discount conditions confusing",
        "promotion differs from app", "offer not applied", "bogo not applied"
    ]),
    "positive_feedback": (None, [
        "staff were helpful and the store was clean", "checkout was quick today thanks",
        "good service and products were available", "app worked well and order was ready",
        "helpful staff answered my question", "store was clean", "good service", "helpful staff"
    ])
}

HIGH_POLICY_ISSUES = {
    "allergen_mislabel", "freezer_cold_chain", "hygiene_pest",
    "staff_misconduct", "workplace_safety", "expired_goods"
}

HIGH_POLICY_KEYWORDS = [
    "allergen", "allergy", "peanut", "gluten", "food poisoning", "poisoning",
    "contamination", "contaminated", "hygiene", "cockroach", "rat", "pest",
    "spoiled", "safety", "unsafe", "abusive", "harass", "misconduct",
    "slip hazard", "unsafe ladder", "blocked emergency exit", "emergency exit",
    "sparking", "electric shock", "expired product", "stale product", "outdated goods"
]

MEDIUM_POLICY_KEYWORDS = [
    "broken", "not working", "billing", "charged twice", "stockout",
    "out of stock", "long wait", "delay", "freezes", "failed",
    "overheating", "refund", "damaged", "leak", "crushed"
]

ALIASES = {
    "record_id": ["record_id", "feedback_id", "id", "ticket_id"],
    "store_id": ["store_id", "store", "location_id", "branch_id"],
    "date": ["date", "created_at", "timestamp", "feedback_date"],
    "text": ["text", "feedback", "comment", "review", "message", "transcript", "note", "content"],
    "channel": ["channel", "source", "feedback_channel"],
    "region": ["region", "area", "territory"],
    "transactions": ["avg_weekly_transactions", "transactions", "weekly_transactions", "feedback_exposure", "store_size"]
}


def normalise(s):
    """Normalize text by stripping URLs, unneeded special characters, while preserving multilingual Hinglish tokens."""
    s = str(s or "").lower().replace("’", "'")
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"[^a-z0-9\u0900-\u097f\u0b80-\u0bff\s']", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def load_taxonomy(taxonomy_source=None):
    """
    Load operational taxonomy and owning function mappings from file, DataFrame, or fallback dictionary.
    Returns: dict mapping issue_type -> (owning_function, list_of_example_phrases)
    """
    if taxonomy_source is None:
        # Search common paths
        candidate_paths = [
            "synthetic_issue_taxonomy.csv",
            os.path.join("..", "data", "synthetic_issue_taxonomy.csv"),
            os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_issue_taxonomy.csv")
        ]
        for p in candidate_paths:
            if os.path.exists(p):
                taxonomy_source = p
                break

    if isinstance(taxonomy_source, str) and os.path.exists(taxonomy_source):
        df = pd.read_csv(taxonomy_source)
    elif isinstance(taxonomy_source, pd.DataFrame):
        df = taxonomy_source
    else:
        return DEFAULT_TAXONOMY

    loaded = {}
    for _, r in df.iterrows():
        iss = str(r["issue_type"]).strip()
        owner = r["owning_function"]
        owner_str = str(owner).strip() if pd.notna(owner) and str(owner).strip() not in ["None", "nan", ""] else None
        phrases = [p.strip().lower() for p in str(r.get("example_phrases", "")).split("|") if p.strip()]
        loaded[iss] = (owner_str, phrases)
    return loaded if len(loaded) >= 10 else DEFAULT_TAXONOMY


class TaxonomyClassifier:
    """Lightweight character and token n-gram classifier for high-accuracy operational taxonomy routing."""
    def __init__(self, taxonomy):
        self.taxonomy = taxonomy
        self.corpus_phrases = []
        self.corpus_issues = []
        self.corpus_owners = []

        for issue, (owner, phrases) in taxonomy.items():
            for p in phrases:
                self.corpus_phrases.append(p)
                self.corpus_issues.append(issue)
                self.corpus_owners.append(owner)

        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))
        self.X_corpus = self.vectorizer.fit_transform(self.corpus_phrases)

    def predict(self, texts):
        if len(texts) == 0:
            return []
        norm_texts = [str(t).lower() for t in texts]
        X_query = self.vectorizer.transform(norm_texts)
        sims = cosine_similarity(X_query, self.X_corpus)
        best_indices = np.argmax(sims, axis=1)
        best_sims = np.max(sims, axis=1)

        results = []
        for idx, (best_i, sim) in enumerate(zip(best_indices, best_sims)):
            if sim >= 0.15:
                results.append((self.corpus_issues[best_i], self.corpus_owners[best_i], float(sim)))
            else:
                results.append(("other_or_unclassified", "Store Ops", float(sim)))
        return results


_GLOBAL_CLASSIFIER = None

def get_classifier(taxonomy=None):
    global _GLOBAL_CLASSIFIER
    if _GLOBAL_CLASSIFIER is None:
        tax = taxonomy or load_taxonomy()
        _GLOBAL_CLASSIFIER = TaxonomyClassifier(tax)
    return _GLOBAL_CLASSIFIER


def prepare_feedback(raw, store_master=None):
    """
    Ingest, normalize columns, join store master exposure and parse dates into ISO / weekly buckets.
    """
    d = raw.copy()
    for key, aliases in ALIASES.items():
        c = next((x for x in aliases if x in d.columns), None)
        if c and c != key:
            d[key] = d[c]
        elif not c:
            d[key] = "" if key not in ["store_id", "transactions"] else ("UNKNOWN" if key == "store_id" else np.nan)

    # Auto-load synthetic_store_master if not provided
    if store_master is None:
        candidate_store_paths = [
            "synthetic_store_master.csv",
            os.path.join("..", "data", "synthetic_store_master.csv"),
            os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_store_master.csv")
        ]
        for p in candidate_store_paths:
            if os.path.exists(p):
                try:
                    store_master = pd.read_csv(p)
                    break
                except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError):
                    continue

    d["record_id"] = d["record_id"].fillna("").astype(str)
    for i in d.index[d["record_id"].isin(["", "nan", "None"])]:
        d.loc[i, "record_id"] = "row_" + str(i)

    d["text"] = d["text"].fillna("").astype(str)
    d["normalised_text"] = d["text"].map(normalise)
    d["date_parsed"] = pd.to_datetime(d["date"], errors="coerce")
    d["store_id"] = d["store_id"].fillna("UNKNOWN").astype(str)

    if "week_start" not in d.columns or d["week_start"].isna().any():
        d["week_start"] = d["date_parsed"].dt.to_period("W").dt.start_time

    # Merge store master metadata if available
    if store_master is not None and not store_master.empty:
        sk = next((c for c in ["store_id", "store", "location_id"] if c in store_master.columns), None)
        if sk:
            sm = store_master.rename(columns={sk: "store_id"})
            # Identify columns to safely bring over
            for col in ["region", "store_name", "store_size", "avg_weekly_transactions"]:
                if col in sm.columns and (col not in d.columns or d[col].isna().all() or (d[col] == "").all()):
                    col_map = sm.set_index("store_id")[col].to_dict()
                    d[col] = d["store_id"].map(col_map)
            if ("transactions" not in d or d["transactions"].isna().all()) and "avg_weekly_transactions" in d.columns:
                d["transactions"] = d["avg_weekly_transactions"]

    return d


def score_feedback(d, taxonomy=None):
    """
    Score feedback with operational classification, policy-first severity override, owning function,
    actionable flag and operational escalation rule.
    """
    o = d.copy()
    if o.empty:
        for c in ["issue_type", "owner", "severity", "actionable", "confidence", "escalation_rule"]:
            o[c] = pd.Series(dtype=object)
        return o
    clf = get_classifier(taxonomy)
    preds = clf.predict(o["text"])

    issues = []
    owners = []
    sevs = []
    acts = []
    confs = []
    rules = []

    for idx, (r, (pred_issue, pred_owner, sim)) in enumerate(zip(o.iterrows(), preds)):
        row = r[1]
        t = row["normalised_text"]
        raw_t = str(row["text"]).lower()

        # Check positive sentiment indicators
        is_positive = (pred_issue == "positive_feedback") or ("clean" in t and "helpful" in t) or ("good service" in t)

        # Policy checks
        has_high_issue = pred_issue in HIGH_POLICY_ISSUES
        has_high_kw = any(k in t or k in raw_t for k in HIGH_POLICY_KEYWORDS)
        has_med_kw = any(k in t or k in raw_t for k in MEDIUM_POLICY_KEYWORDS)

        # Severity determination
        if is_positive:
            sev = "LOW"
            act = False
            rule = "Positive feedback logged; no corrective operational action required."
            conf = min(0.99, max(0.85, sim))
        elif has_high_issue or has_high_kw:
            sev = "HIGH"
            act = True
            rule = "Immediate escalation: safety/allergen/hygiene/cold-chain/staff-misconduct policy override."
            conf = min(0.98, max(0.88, sim + 0.1))
        elif has_med_kw or sim >= 0.40:
            sev = "MEDIUM"
            act = True
            rule = "Owner review in next operational cycle."
            conf = round(min(0.92, max(0.65, sim)), 2)
        else:
            sev = "LOW"
            act = False
            rule = "Monitor; escalate if repeated, corroborated or rapidly increasing."
            conf = round(max(0.40, sim), 2)

        issues.append(pred_issue)
        owners.append(pred_owner)
        sevs.append(sev)
        acts.append(act)
        confs.append(round(conf, 2))
        rules.append(rule)

    o["issue_type"] = issues
    o["owner"] = owners
    o["severity"] = sevs
    o["actionable"] = acts
    o["confidence"] = confs
    o["escalation_rule"] = rules
    return o


def get_canonical_signature(text):
    """Extract canonical semantic signature from feedback by removing greetings, Hinglish fillers, and punctuation."""
    t = str(text or "").lower()
    t = re.sub(r"^(today|really|fyi|not happy —|not happy -|urgent:|urgent|please fix:|please fix|again,)\s*", "", t)
    t = re.sub(r"(yaar bahut problem hai|bilkul theek nahi hai|staff ko bata diya|phir se same issue|customer pareshan hai|jaldi paarunga|koi sun nahi raha)", "", t)
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def deduplicate_records(d):
    """
    Conservative deduplication: identifies records from the same store on the same calendar day
    sharing near-identical canonical text signatures.
    Adds 'duplicate_group', 'is_duplicate' (False for primary, True for duplicates) and 'duplicate_count'.
    """
    o = d.copy()
    seen = {}
    counts = {}
    groups = []
    is_dups = []

    sigs = [get_canonical_signature(t) for t in o["text"]]
    dates = pd.to_datetime(o["date_parsed"]).dt.date.astype(str)
    stores = o["store_id"].astype(str)

    for i, (st, dt, sig) in enumerate(zip(stores, dates, sigs)):
        if len(sig) < 4:
            sig = f"raw_{i}"
        key = (st, dt, sig)
        if key not in seen:
            grp_id = f"dup_{st}_{dt.replace('-', '')}_{hashlib.md5(sig.encode()).hexdigest()[:6]}"
            seen[key] = grp_id
            counts[grp_id] = 1
            groups.append(grp_id)
            is_dups.append(False)
        else:
            grp_id = seen[key]
            counts[grp_id] += 1
            groups.append(grp_id)
            is_dups.append(True)

    o["duplicate_group"] = groups
    o["is_duplicate"] = is_dups
    o["duplicate_count"] = [counts[g] for g in groups]
    return o


def emerging_incidents(d, min_ratio=1.75, min_count=2, lookback_weeks=2, latest_only=False):
    """
    Store-level emerging incident radar: detects surging or sustained operational anomalies
    using multi-week baseline ratios and exposure normalization.
    """
    if "date_parsed" not in d or d["date_parsed"].isna().all():
        return pd.DataFrame()

    x = d[d["date_parsed"].notna()].copy()
    if "week_start" not in x:
        x["week_start"] = x["date_parsed"].dt.to_period("W").dt.start_time

    weeks = sorted(x["week_start"].unique())
    if len(weeks) < 2:
        return pd.DataFrame()

    stores = x["store_id"].unique()
    issues = [iss for iss in x["issue_type"].unique() if iss != "positive_feedback"]

    # Weekly aggregation
    g = x[x["issue_type"] != "positive_feedback"].groupby(["store_id", "issue_type", "week_start"]).size().rename("count").reset_index()

    # Create complete grid across all weeks
    idx = pd.MultiIndex.from_product([stores, issues, weeks], names=["store_id", "issue_type", "week_start"])
    full = g.set_index(["store_id", "issue_type", "week_start"]).reindex(idx, fill_value=0).reset_index()

    # Join transaction exposure
    exp_col = next((c for c in ["transactions", "avg_weekly_transactions", "weekly_transactions"] if c in x.columns), None)
    if exp_col:
        trans_map = x.groupby("store_id")[exp_col].first().to_dict()
        full["transactions"] = full["store_id"].map(trans_map).fillna(2000)
    else:
        full["transactions"] = 2000

    full["rate_per_1k"] = full["count"] / pd.to_numeric(full["transactions"], errors="coerce").replace(0, np.nan) * 1000

    # Strictly causal rolling and expanding baseline (strictly prior weeks via shift(1); zero future-data leakage)
    full = full.sort_values(["store_id", "issue_type", "week_start"])
    full["prev_avg_count"] = full.groupby(["store_id", "issue_type"])["count"].shift(1).rolling(lookback_weeks, min_periods=1).mean().fillna(0.0)
    full["prev_exp_mean"] = full.groupby(["store_id", "issue_type"])["count"].shift(1).expanding(min_periods=1).mean().fillna(0.0)
    full["growth_ratio"] = (full["count"] + 0.5) / (full["prev_avg_count"] + 0.5)

    # Condition: Growth surge OR sustained elevated volume for high policy issues
    surge_cond = (full["growth_ratio"] >= min_ratio) & (full["count"] >= min_count)
    sustained_cond = full["issue_type"].isin(HIGH_POLICY_ISSUES) & (full["count"] >= 3) & (full["count"] > full["prev_exp_mean"] * 1.3)

    radar = full[surge_cond | sustained_cond].copy()
    if radar.empty:
        return pd.DataFrame()

    if latest_only:
        latest_week = weeks[-1]
        radar = radar[radar["week_start"] == latest_week]
        if radar.empty:
            return pd.DataFrame()

    # Alert levels and reasons
    radar["alert_level"] = np.where(
        radar["issue_type"].isin(HIGH_POLICY_ISSUES) & ((radar["growth_ratio"] >= 2.5) | (radar["count"] >= 3)),
        "CRITICAL", "WARNING"
    )
    radar["growth_ratio"] = radar["growth_ratio"].round(2)
    radar["prev_avg_count"] = radar["prev_avg_count"].round(1)
    radar["rate_per_1k"] = radar["rate_per_1k"].round(2)
    radar["absolute_change"] = (radar["count"] - radar["prev_avg_count"]).round(1)

    radar["alert_reason"] = (
        radar["growth_ratio"].astype(str) + "x prior " + str(lookback_weeks) + "-wk baseline (" +
        radar["prev_avg_count"].astype(str) + " -> " + radar["count"].astype(str) + " records; " +
        radar["rate_per_1k"].astype(str) + "/1k trans)"
    )
    radar["measure_note"] = "Exposure-normalised weekly rate" if exp_col else "Count proxy; add store exposure"

    # Add store name / region if present in original data
    for col in ["store_name", "region"]:
        if col in x.columns:
            meta = x.groupby("store_id")[col].first().to_dict()
            radar[col] = radar["store_id"].map(meta)

    # Map owning function
    owner_map = {iss: info[0] for iss, info in DEFAULT_TAXONOMY.items()}
    radar["owner"] = radar["issue_type"].map(owner_map).fillna("Store Ops")

    cols = ["store_id"]
    if "store_name" in radar.columns:
        cols.append("store_name")
    if "region" in radar.columns:
        cols.append("region")
    cols += [
        "issue_type", "owner", "week_start", "count", "prev_avg_count", "growth_ratio",
        "absolute_change", "rate_per_1k", "alert_level", "alert_reason", "measure_note"
    ]
    return radar[cols].sort_values(by=["week_start", "alert_level", "growth_ratio"], ascending=[False, True, False])


def build_weekly_brief(d, region=None, week=None):
    """
    Generate an executive-ready Voice-of-Store Weekly Action Brief.
    """
    x = d.copy()
    if region is not None and region != "All":
        x = x[x["region"].astype(str) == str(region)]
    if week is not None and "week_start" in x.columns:
        x = x[x["week_start"].astype(str) == str(week)]

    if x.empty:
        return "No feedback records found for the selected region and timeframe."

    hi = x[x["severity"] == "HIGH"]
    act = x[x["actionable"] == True]
    dup_count = int(x["is_duplicate"].sum()) if "is_duplicate" in x.columns else 0

    lines = [
        f"### 📋 Voice-of-Store Weekly Brief — {region or 'All Regions'}",
        "*Operational summary of store chatter, safety risks, and frontline feedback.*",
        "",
        "#### Key Operational Metrics",
        f"- **Total Records Reviewed:** {len(x):,}",
        f"- **High-Severity Risk Escalations:** {len(hi):,} ({len(hi)/len(x)*100:.1f}%)",
        f"- **Actionable Operational Items:** {len(act):,} ({len(act)/len(x)*100:.1f}%)",
        f"- **Conservative Near-Duplicates Identified:** {dup_count:,}",
        "",
        "#### Top Operational Issue Categories & Owning Functions"
    ]

    issue_summary = x[x["issue_type"] != "positive_feedback"].groupby(["issue_type", "owner"]).size().sort_values(ascending=False).head(5)
    for (issue, owner), n in issue_summary.items():
        sample_quotes = x[x["issue_type"] == issue]["text"].head(2).tolist()
        clean_quotes = [f"“{str(q).strip()[:110]}”" for q in sample_quotes if str(q).strip()]
        quote_str = " | ".join(clean_quotes) if clean_quotes else "No text quote available"
        lines.append(f"- **{issue.replace('_', ' ').title()}** ({n} records, {n/len(x)*100:.1f}%) — **Owner: {owner}**")
        lines.append(f"  *Evidence:* {quote_str}")

    lines.extend([
        "",
        "#### Escalation Policy & Routing Guidance",
        "- **HIGH:** Immediate same-day triage for statutory risks, cold chain, food safety, allergen mislabeling, or staff harassment.",
        "- **MEDIUM:** Functional owner review (Store Ops / Supply Chain / Digital / Merchandising) in the next weekly sprint.",
        "- **LOW / Positive:** Tracked for trend corroboration; positive feedback logged for team recognition."
    ])

    return "\n".join(lines)


def evaluate_incident_lead_time(radar_df, manifest_df, feedback_df=None):
    """
    Measure detection lead time and delay for synthetic incidents against the incident manifest.
    Computes lead time compared to a standard 30-day monthly batch review baseline.
    """
    if radar_df.empty or manifest_df.empty:
        return pd.DataFrame()

    min_date = pd.to_datetime(feedback_df["date"]).min() if feedback_df is not None and "date" in feedback_df else pd.to_datetime(radar_df["week_start"]).min()

    results = []
    for _, inc in manifest_df.iterrows():
        inc_id = inc["incident_id"]
        st = inc["store_id"]
        iss = inc["issue_type"]
        sday = int(inc["start_day"])
        pattern = inc.get("pattern", "unknown")

        onset_date = min_date + pd.Timedelta(days=sday)
        st_alerts = radar_df[(radar_df["store_id"] == st) & (radar_df["issue_type"] == iss)].sort_values("week_start", ascending=True)
        post_onset = st_alerts[pd.to_datetime(st_alerts["week_start"]) >= (onset_date - pd.Timedelta(days=7))]

        if not post_onset.empty:
            first_alert = post_onset.iloc[0]
            alert_week = pd.to_datetime(first_alert["week_start"])
            alert_day = (alert_week - min_date).total_seconds() / 86400
            detection_delay = alert_day - sday
            lead_time_vs_monthly = 30.0 - max(0.0, detection_delay)

            results.append({
                "incident_id": inc_id,
                "store_id": st,
                "issue_type": iss,
                "pattern": pattern,
                "start_day": sday,
                "onset_date": str(onset_date.date()),
                "detected_week": str(alert_week.date()),
                "alert_level": first_alert.get("alert_level", "WARNING"),
                "surge_ratio": first_alert.get("growth_ratio", np.nan),
                "count": first_alert.get("count", np.nan),
                "detection_delay_days": round(detection_delay, 1),
                "lead_time_vs_monthly_days": round(lead_time_vs_monthly, 1),
                "status": "DETECTED"
            })
        else:
            results.append({
                "incident_id": inc_id,
                "store_id": st,
                "issue_type": iss,
                "pattern": pattern,
                "start_day": sday,
                "onset_date": str(onset_date.date()),
                "detected_week": "N/A",
                "alert_level": "None",
                "surge_ratio": np.nan,
                "count": 0,
                "detection_delay_days": np.nan,
                "lead_time_vs_monthly_days": 0.0,
                "status": "MISSED"
            })

    return pd.DataFrame(results)
