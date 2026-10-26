import os

import pandas as pd
import streamlit as st
from engine import (
    build_weekly_brief,
    deduplicate_records,
    emerging_incidents,
    load_taxonomy,
    prepare_feedback,
    score_feedback,
)
from styles import APPLE_CSS, render_header, render_seeded_incident_card

# -----------------------------------------------------------------------------
# 1. Page Configuration & Apple HIG Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="VoicePulse AI · Enterprise Engine",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Apple Human Interface Guidelines Design Tokens & Styles
st.markdown(APPLE_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. File Paths & Data Directories
# -----------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DEFAULT_40K_PATH = os.path.join(DATA_DIR, "synthetic_feedback_40000.csv")
DEFAULT_4K_PATH = os.path.join(DATA_DIR, "synthetic_validation_4000.csv")
DEFAULT_STORE_MASTER = os.path.join(DATA_DIR, "synthetic_store_master.csv")
DEFAULT_TAXONOMY = os.path.join(DATA_DIR, "synthetic_issue_taxonomy.csv")
SAMPLE_CSV_PATH = os.path.join(os.path.dirname(__file__), "sample_feedback.csv")

# -----------------------------------------------------------------------------
# 3. Sidebar: Product Identity, Navigation & Data Configuration
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 12px 4px 18px 4px; border-bottom: 1px solid var(--apple-border); margin-bottom: 18px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 38px; height: 38px; border-radius: 10px; background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 19px; box-shadow: 0 2px 6px rgba(0, 122, 255, 0.3);">📡</div>
            <div>
                <div style="font-weight: 600; font-size: 16px; color: var(--apple-text-primary); letter-spacing: -0.01em;">VoicePulse AI</div>
                <div style="font-size: 11px; color: var(--apple-text-secondary); text-transform: uppercase; letter-spacing: 0.04em;">Enterprise v2.6 · R5</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Navigation")
    nav_sections = [
        "Executive Overview",
        "Frontline Triage",
        "Incident Radar",
        "Regional Intelligence",
        "Reports & Exports",
        "Complete Unified View"
    ]
    selected_nav = st.radio(
        "Navigate Dashboard",
        nav_sections,
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("### Data Source")

    dataset_options = [
        "Synthetic 40,000 Dataset (Full Benchmark)",
        "Synthetic 4,000 Validation Sample",
        "Quick Smoke-Test Sample (10 records)",
        "Upload Custom CSV"
    ]
    selected_dataset = st.selectbox(
        "Active Feedback Dataset",
        dataset_options,
        index=0,
        label_visibility="collapsed"
    )

    uploaded_file = None
    if selected_dataset == "Upload Custom CSV":
        uploaded_file = st.file_uploader("Upload Feedback CSV", type=["csv"])

    with st.expander("⚙️ Advanced Data Overrides", expanded=False):
        store_file = st.file_uploader("Custom Store Master CSV", type=["csv"], key="custom_store")
        tax_file = st.file_uploader("Custom Issue Taxonomy CSV", type=["csv"], key="custom_tax")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: var(--apple-surface); border: 1px solid var(--apple-border); border-radius: var(--apple-radius-sm); padding: 12px; font-size: 12px; color: var(--apple-text-secondary);">
        <div style="font-weight: 600; color: var(--apple-text-primary); margin-bottom: 4px;">System Health</div>
        <div>• Model: Hybrid TF-IDF & Rules</div>
        <div>• Taxonomy: 31 operational classes</div>
        <div>• Policy Engine: Same-day SLA active</div>
        <div>• Store Normalization: ISO-week rate</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. Cached Pipeline Execution
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_and_process_data(dataset_choice, uploaded_bytes, store_bytes, tax_bytes):
    # 1. Load Feedback Data
    if dataset_choice == "Upload Custom CSV":
        if uploaded_bytes is None:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        raw_df = pd.read_csv(uploaded_bytes)
    elif dataset_choice == "Synthetic 40,000 Dataset (Full Benchmark)":
        if os.path.exists(DEFAULT_40K_PATH):
            raw_df = pd.read_csv(DEFAULT_40K_PATH)
        else:
            raw_df = pd.read_csv(SAMPLE_CSV_PATH)
    elif dataset_choice == "Synthetic 4,000 Validation Sample":
        if os.path.exists(DEFAULT_4K_PATH):
            raw_df = pd.read_csv(DEFAULT_4K_PATH)
        else:
            raw_df = pd.read_csv(SAMPLE_CSV_PATH)
    else:
        raw_df = pd.read_csv(SAMPLE_CSV_PATH)

    # 2. Load Store Master
    store_df = None
    if store_bytes is not None:
        store_df = pd.read_csv(store_bytes)
    elif os.path.exists(DEFAULT_STORE_MASTER):
        store_df = pd.read_csv(DEFAULT_STORE_MASTER)

    # 3. Load Taxonomy
    tax_dict = None
    if tax_bytes is not None:
        tax_df = pd.read_csv(tax_bytes)
        tax_dict = load_taxonomy(tax_df)
    elif os.path.exists(DEFAULT_TAXONOMY):
        tax_dict = load_taxonomy(DEFAULT_TAXONOMY)

    # 4. Process Pipeline
    prepared = prepare_feedback(raw_df, store_master=store_df)
    scored = score_feedback(prepared, taxonomy=tax_dict)
    deduped = deduplicate_records(scored)
    radar = emerging_incidents(deduped)

    # Pre-generate export bytes inside cached pipeline for instant downloads
    scored_csv = deduped.to_csv(index=False).encode("utf-8")
    radar_csv = radar.to_csv(index=False).encode("utf-8")

    return raw_df, deduped, radar, scored_csv, radar_csv

with st.spinner("Processing store feedback signals through VoicePulse Engine..."):
    raw_input, scored_df, radar_df, cached_scored_csv, cached_radar_csv = load_and_process_data(
        selected_dataset,
        uploaded_file if uploaded_file else None,
        store_file if 'store_file' in locals() and store_file else None,
        tax_file if 'tax_file' in locals() and tax_file else None
    )

if raw_input.empty:
    st.info("Please select or upload a valid feedback CSV dataset to begin analysis.")
    st.stop()

# -----------------------------------------------------------------------------
# 5. Top Executive Header Bar & Context Banner
# -----------------------------------------------------------------------------
dataset_label = (
    "Synthetic 40k Benchmark" if "40,000" in selected_dataset
    else "4k Validation Sample" if "4,000" in selected_dataset
    else "Smoke-Test Sample" if "10" in selected_dataset
    else "Custom Uploaded CSV"
)

st.markdown(render_header(total_records=len(scored_df), active_source=dataset_label), unsafe_allow_html=True)

# Synthetic Disclosure Notice (Apple-styled subtle callout)
st.markdown("""
<div style="background: var(--apple-surface); border: 1px solid var(--apple-border); border-radius: var(--apple-radius-md); padding: 12px 18px; margin-bottom: 22px; display: flex; align-items: center; justify-content: space-between; gap: 12px; box-shadow: var(--apple-shadow-card);">
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 16px;">💡</span>
        <span style="font-size: 13px; color: var(--apple-text-secondary);">
            <strong style="color: var(--apple-text-primary);">Connected Data Stream:</strong> Ingesting 31-class operational taxonomy, store master transaction exposures, and policy-first severity escalation.
        </span>
    </div>
    <span class="apple-badge apple-badge-gray" style="white-space: nowrap;">Synthetic Local Evaluation</span>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Section 1: Executive Overview & High-Level KPIs
# -----------------------------------------------------------------------------
show_overview = selected_nav in ["Executive Overview", "Complete Unified View"]

if show_overview:
    st.markdown('<div class="apple-section-title">1 · Executive Overview & Operational Pulse</div>', unsafe_allow_html=True)

    total_records = len(scored_df)
    high_sev_count = int((scored_df["severity"] == "HIGH").sum())
    actionable_count = int(scored_df["actionable"].sum())
    dup_count = int(scored_df["is_duplicate"].sum()) if "is_duplicate" in scored_df else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Feedback Records",
            value=f"{total_records:,}",
            help="Total frontline records ingested across customer reviews, shift notes, and call logs."
        )

    with col2:
        high_pct = (high_sev_count / total_records * 100) if total_records > 0 else 0
        st.metric(
            label="High-Severity Policy Risks",
            value=f"{high_sev_count:,}",
            delta=f"{high_pct:.1f}% volume",
            delta_color="inverse",
            help="Statutory, life safety, food safety, or harassment complaints requiring immediate action."
        )

    with col3:
        act_pct = (actionable_count / total_records * 100) if total_records > 0 else 0
        st.metric(
            label="Actionable Operational Tickets",
            value=f"{actionable_count:,}",
            delta=f"{act_pct:.1f}% volume",
            delta_color="normal",
            help="Complaints and operational disruptions requiring owning-function intervention."
        )

    with col4:
        dup_pct = (dup_count / total_records * 100) if total_records > 0 else 0
        st.metric(
            label="Near-Duplicates Flagged",
            value=f"{dup_count:,}",
            delta=f"{dup_pct:.1f}% duplicates",
            delta_color="off",
            help="Secondary records identified sharing same store, date, and semantic canonical text."
        )

    # Operational Distribution Widgets
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    d_col1, d_col2 = st.columns(2)

    with d_col1, st.container(border=True):
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span class="apple-card-title">Feedback Channels</span>
            <span class="apple-badge apple-badge-blue">Ingestion Mix</span>
        </div>
        """, unsafe_allow_html=True)
        if "channel" in scored_df.columns:
            ch_dist = scored_df["channel"].value_counts().reset_index()
            ch_dist.columns = ["Channel", "Records"]
            ch_dist["Share"] = (ch_dist["Records"] / total_records).round(3)
            st.dataframe(
                ch_dist,
                column_config={
                    "Channel": st.column_config.TextColumn("Channel"),
                    "Records": st.column_config.NumberColumn("Record Volume", format="%d"),
                    "Share": st.column_config.ProgressColumn("Volume Share", min_value=0.0, max_value=1.0, format="%.1f%%")
                },
                width="stretch",
                hide_index=True
            )

    with d_col2, st.container(border=True):
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span class="apple-card-title">Owning Function Routing</span>
            <span class="apple-badge apple-badge-green">Operational Ownership</span>
        </div>
        """, unsafe_allow_html=True)
        if "owner" in scored_df.columns:
            owner_dist = scored_df[scored_df["owner"] != "None"]["owner"].value_counts().reset_index()
            owner_dist.columns = ["Function", "Assigned Tickets"]
            owner_dist["Share"] = (owner_dist["Assigned Tickets"] / total_records).round(3)
            st.dataframe(
                owner_dist,
                column_config={
                    "Function": st.column_config.TextColumn("Owning Function"),
                    "Assigned Tickets": st.column_config.NumberColumn("Tickets", format="%d"),
                    "Share": st.column_config.ProgressColumn("Share", min_value=0.0, max_value=1.0, format="%.1f%%")
                },
                width="stretch",
                hide_index=True
            )

    with st.expander("🔍 Ingested Raw Schema Preview (First 10 Records)", expanded=False):
        st.dataframe(raw_input.head(10), width="stretch")

# -----------------------------------------------------------------------------
# Section 2: Frontline Triage & Owning-Function Routing
# -----------------------------------------------------------------------------
show_triage = selected_nav in ["Frontline Triage", "Complete Unified View"]

if show_triage:
    st.markdown('<div class="apple-section-title">2 · Frontline Triage & Owning-Function Routing</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span class="apple-card-title">Filter Operational Queue</span>
            <span class="apple-badge apple-badge-gray">Real-time Filtering</span>
        </div>
        """, unsafe_allow_html=True)

        f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 2.0, 1.8, 1.2])

        with f_col1:
            severity_filters = st.multiselect(
                "Severity Tiers",
                ["HIGH", "MEDIUM", "LOW"],
                default=["HIGH", "MEDIUM", "LOW"]
            )

        with f_col2:
            available_owners = sorted([str(o) for o in scored_df["owner"].dropna().unique() if str(o) != "None"])
            owner_filters = st.multiselect(
                "Owning Function",
                available_owners,
                default=available_owners
            )

        with f_col3:
            available_channels = sorted(scored_df["channel"].dropna().astype(str).unique())
            channel_filters = st.multiselect(
                "Channel Source",
                available_channels,
                default=available_channels
            )

        with f_col4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            hide_dups = st.checkbox("Hide Duplicates", value=False, help="Filter out secondary records from conservative duplicate groups")

    # Search Box
    search_query = st.text_input("Search records by keyword, store ID, or text verbatim:", placeholder="e.g. 'cold chain', 'ST017', 'allergen', 'billing'...")

    # Filter Logic
    filtered_df = scored_df[
        (scored_df["severity"].isin(severity_filters)) &
        (scored_df["channel"].astype(str).isin(channel_filters))
    ]

    if owner_filters:
        filtered_df = filtered_df[filtered_df["owner"].astype(str).isin(owner_filters) | (filtered_df["issue_type"] == "positive_feedback")]

    if hide_dups and "is_duplicate" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["is_duplicate"] == False]

    if search_query.strip():
        q = search_query.strip().lower()
        filtered_df = filtered_df[
            filtered_df["text"].astype(str).str.lower().str.contains(q, na=False) |
            filtered_df["store_id"].astype(str).str.lower().str.contains(q, na=False) |
            filtered_df["issue_type"].astype(str).str.lower().str.contains(q, na=False)
        ]

    # Data Table Presentation with Column Config
    display_cols = [
        "record_id", "date", "store_id", "channel", "text",
        "issue_type", "severity", "owner", "actionable", "confidence", "escalation_rule"
    ]
    avail_cols = [c for c in display_cols if c in filtered_df.columns]
    
    st.dataframe(
        filtered_df[avail_cols].head(500),
        column_config={
            "record_id": st.column_config.TextColumn("Ticket ID", width="small"),
            "date": st.column_config.DateColumn("Date", width="small"),
            "store_id": st.column_config.TextColumn("Store", width="small"),
            "channel": st.column_config.TextColumn("Channel", width="small"),
            "text": st.column_config.TextColumn("Frontline Feedback Verbatim", width="large"),
            "issue_type": st.column_config.TextColumn("Classified Issue", width="medium"),
            "severity": st.column_config.TextColumn("Severity", width="small"),
            "owner": st.column_config.TextColumn("Owner", width="small"),
            "actionable": st.column_config.CheckboxColumn("Actionable", width="small"),
            "confidence": st.column_config.ProgressColumn("Confidence", min_value=0.0, max_value=1.0, format="%.2f", width="small"),
            "escalation_rule": st.column_config.TextColumn("Escalation SLA", width="medium"),
        },
        width="stretch",
        hide_index=True
    )
    st.caption(f"Showing top {min(len(filtered_df), 500):,} matching records out of {len(filtered_df):,} filtered results.")

    # Interactive Live Classification Tester
    with st.expander("🧪 Test Live Classification & Policy Escalation Engine", expanded=False):
        st.markdown("Type any sample customer feedback or store shift observation below to test real-time classification, routing, and escalation rules:")
        test_input = st.text_input(
            "Sample Frontline Text:",
            value="freezer in dairy section stopped cooling, milk packets are warm"
        )
        if test_input.strip():
            single_df = pd.DataFrame([{"record_id": "TEST-001", "store_id": "ST017", "date": "2026-03-01", "text": test_input, "channel": "customer_review"}])
            scored_single = score_feedback(prepare_feedback(single_df))
            
            res_row = scored_single.iloc[0]
            r1, r2, r3, r4, r5 = st.columns(5)
            r1.metric("Classified Issue", str(res_row["issue_type"]))
            r2.metric("Severity Level", str(res_row["severity"]))
            r3.metric("Owning Function", str(res_row["owner"]))
            r4.metric("Actionable", "YES" if res_row["actionable"] else "NO")
            r5.metric("Model Confidence", f"{res_row['confidence']:.2f}")
            st.info(f"**Escalation Policy:** {res_row['escalation_rule']}")

# -----------------------------------------------------------------------------
# Section 3: Store-Level Emerging Incident Radar
# -----------------------------------------------------------------------------
show_radar = selected_nav in ["Incident Radar", "Complete Unified View"]

if show_radar:
    st.markdown('<div class="apple-section-title">3 · Store-Level Emerging Incident Radar</div>', unsafe_allow_html=True)

    if not radar_df.empty:
        r_col1, r_col2 = st.columns([1, 2.5])
        with r_col1, st.container(border=True):
            st.markdown("""
            <div style="margin-bottom: 12px;">
                <span class="apple-card-title">Radar Controls</span>
            </div>
            """, unsafe_allow_html=True)
            
            radar_mode = st.radio(
                "View Mode",
                ["Latest Active Week Alerts", "Full Timeline (Historical Surge Radar)", "Seeded Synthetic Incidents (Audit View)"]
            )
            min_alert_level = st.multiselect(
                "Alert Priority Level",
                ["CRITICAL", "WARNING"],
                default=["CRITICAL", "WARNING"]
            )
            store_filter = st.multiselect(
                "Filter by Store ID",
                sorted(radar_df["store_id"].unique()),
                default=[]
            )

        radar_display = radar_df[radar_df["alert_level"].isin(min_alert_level)].copy()
        if radar_mode == "Latest Active Week Alerts":
            latest_week = radar_display["week_start"].max()
            radar_display = radar_display[radar_display["week_start"] == latest_week]
        elif radar_mode == "Seeded Synthetic Incidents (Audit View)":
            radar_display = radar_display[radar_display["store_id"].isin(["ST017", "ST042", "ST088"])]
        elif store_filter:
            radar_display = radar_display[radar_display["store_id"].isin(store_filter)]

        with r_col2, st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="apple-card-title">Multi-Week Exposure-Normalised Surge Detection</span>
                <span class="apple-badge apple-badge-blue">Incident Heuristics</span>
            </div>
            <div style="font-size: 13px; color: var(--apple-text-secondary); line-height: 1.5; margin-bottom: 12px;">
                Compares weekly issue rates per 1,000 store transactions against a rolling 2-week baseline.
                Flags rapid acceleration (≥1.75x ratio) or sustained statutory high-severity clusters.
            </div>
            """, unsafe_allow_html=True)

            if not radar_display.empty:
                st.dataframe(
                    radar_display,
                    column_config={
                        "store_id": st.column_config.TextColumn("Store", width="small"),
                        "issue_type": st.column_config.TextColumn("Incident Issue", width="medium"),
                        "owner": st.column_config.TextColumn("Owner", width="small"),
                        "week_start": st.column_config.DateColumn("Week Start", width="small"),
                        "count": st.column_config.NumberColumn("Complaints", format="%d", width="small"),
                        "prev_avg_count": st.column_config.NumberColumn("Prior Baseline", format="%.1f", width="small"),
                        "growth_ratio": st.column_config.NumberColumn("Surge Ratio", format="%.2fx", width="small"),
                        "rate_per_1k": st.column_config.NumberColumn("Rate / 1k Trans", format="%.2f", width="small"),
                        "alert_level": st.column_config.TextColumn("Priority", width="small"),
                        "alert_reason": st.column_config.TextColumn("Alert Rationale", width="large"),
                    },
                    width="stretch",
                    hide_index=True
                )
            else:
                st.info("No emerging anomalies detected matching the active filter criteria.")

        # Dedicated Seeded Synthetic Incident Verification Cards
        if radar_mode == "Seeded Synthetic Incidents (Audit View)":
            st.markdown('<div class="apple-card-title" style="margin-top: 18px; margin-bottom: 10px;">🔍 Seeded Synthetic Incidents — Audit & Verification Cards</div>', unsafe_allow_html=True)
            
            for inc_id, st_id, iss, pat, sday in [
                ("SYNTH_INCIDENT_1", "ST017", "freezer_cold_chain", "Gradual failure", "Day 77"),
                ("SYNTH_INCIDENT_2", "ST042", "allergen_mislabel", "Sharp packaging error", "Day 91"),
                ("SYNTH_INCIDENT_3", "ST088", "staff_misconduct", "Gradual escalation", "Day 98")
            ]:
                sub_ev = scored_df[(scored_df["store_id"] == st_id) & (scored_df["issue_type"] == iss)]
                quotes = [str(t) for t in sub_ev["text"].head(3)]
                owner = sub_ev["owner"].iloc[0] if not sub_ev.empty else "Store Ops"
                
                st.markdown(
                    render_seeded_incident_card(
                        incident_id=inc_id,
                        store_id=st_id,
                        issue_type=iss,
                        owner=owner,
                        pattern=pat,
                        start_day=sday,
                        quotes=quotes,
                        alert_level="CRITICAL"
                    ),
                    unsafe_allow_html=True
                )
    else:
        st.warning("Not enough time-series depth to compute multi-week radar baseline. Provide multiple weeks of store feedback.")

# -----------------------------------------------------------------------------
# Section 4: Regional Weekly Action Brief
# -----------------------------------------------------------------------------
show_brief = selected_nav in ["Regional Intelligence", "Complete Unified View"]

if show_brief:
    st.markdown('<div class="apple-section-title">4 · Regional Weekly Action Brief</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span class="apple-card-title">Select Regional Scope & Timeframe</span>
            <span class="apple-badge apple-badge-blue">Executive Synthesis</span>
        </div>
        """, unsafe_allow_html=True)

        b_col1, b_col2 = st.columns(2)
        with b_col1:
            regions = ["All"] + sorted([str(r) for r in scored_df["region"].dropna().unique() if str(r).strip() not in ["", "nan"]])
            selected_region = st.selectbox("Operating Region", regions, index=0)

        with b_col2:
            if "week_start" in scored_df.columns and scored_df["week_start"].notna().any():
                weeks = ["All Weeks"] + sorted([str(w.date()) if hasattr(w, "date") else str(w)[:10] for w in scored_df["week_start"].dropna().unique()], reverse=True)
                selected_week = st.selectbox("Reporting Week (ISO Monday)", weeks, index=0)
            else:
                selected_week = "All Weeks"

    brief_content = build_weekly_brief(
        scored_df,
        region=None if selected_region == "All" else selected_region,
        week=None if selected_week == "All Weeks" else selected_week
    )

    with st.container(border=True):
        st.markdown(brief_content)

# -----------------------------------------------------------------------------
# Section 5: Data Exports & Artifact Downloads
# -----------------------------------------------------------------------------
show_exports = selected_nav in ["Reports & Exports", "Complete Unified View"]

if show_exports:
    st.markdown('<div class="apple-section-title">5 · Reports & Data Exports</div>', unsafe_allow_html=True)

    brief_text = build_weekly_brief(
        scored_df,
        region=None if 'selected_region' not in locals() or selected_region == "All" else selected_region,
        week=None if 'selected_week' not in locals() or selected_week == "All Weeks" else selected_week
    )

    e1, e2, e3 = st.columns(3)

    with e1, st.container(border=True):
        st.markdown("<div style='font-size: 26px; margin-bottom: 6px;'>📊</div>", unsafe_allow_html=True)
        st.markdown("**Scored Feedback Dataset**")
        st.caption("Complete enriched dataset with classifications, severity, owner, confidence, and deduplication tags.")
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        st.download_button(
            "Download Scored CSV",
            cached_scored_csv,
            "voicepulse_scored_feedback.csv",
            "text/csv",
            use_container_width=True
        )

    with e2, st.container(border=True):
        st.markdown("<div style='font-size: 26px; margin-bottom: 6px;'>🎯</div>", unsafe_allow_html=True)
        st.markdown("**Emerging Radar Alerts**")
        st.caption("Multi-week exposure-normalized surge detection anomalies and statutory risk clusters.")
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        st.download_button(
            "Download Radar Alerts CSV",
            cached_radar_csv,
            "voicepulse_emerging_incidents.csv",
            "text/csv",
            use_container_width=True
        )

    with e3, st.container(border=True):
        st.markdown("<div style='font-size: 26px; margin-bottom: 6px;'>📋</div>", unsafe_allow_html=True)
        st.markdown("**Executive Weekly Brief**")
        st.caption("Executive markdown synthesis with operational metrics, top issues, and frontline quotes.")
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        st.download_button(
            "Download Weekly Brief (MD)",
            brief_text.encode("utf-8"),
            "voicepulse_weekly_brief.md",
            "text/markdown",
            use_container_width=True
        )
