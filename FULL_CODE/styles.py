"""
VoicePulse AI — Apple Human Interface Guidelines (HIG) Design System
Refined light theme, SF Pro typography, modular surfaces, and semantic tokens.
"""

APPLE_CSS = """
<style>
/* =====================================================================
   Apple Human Interface Guidelines Design Tokens & Global Typography
   ===================================================================== */
:root {
  --apple-bg: #F5F5F7;
  --apple-surface: #FFFFFF;
  --apple-surface-hover: #FAFAFC;
  --apple-surface-muted: #F2F2F7;
  --apple-border: #E5E5EA;
  --apple-border-subtle: #F0F0F4;
  --apple-text-primary: #1D1D1F;
  --apple-text-secondary: #6E6E73;
  --apple-text-tertiary: #86868B;
  --apple-blue: #007AFF;
  --apple-blue-soft: rgba(0, 122, 255, 0.08);
  --apple-blue-border: rgba(0, 122, 255, 0.22);
  --apple-indigo: #5856D6;
  --apple-indigo-soft: rgba(88, 86, 214, 0.08);
  --apple-green: #248A3D;
  --apple-green-soft: rgba(36, 138, 61, 0.09);
  --apple-amber: #B76E00;
  --apple-amber-soft: rgba(183, 110, 0, 0.09);
  --apple-red: #D70015;
  --apple-red-soft: rgba(215, 0, 21, 0.08);
  --apple-font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --apple-radius-sm: 8px;
  --apple-radius-md: 12px;
  --apple-radius-lg: 16px;
  --apple-shadow-card: 0 2px 8px rgba(0, 0, 0, 0.03), 0 1px 2px rgba(0, 0, 0, 0.02);
  --apple-shadow-float: 0 8px 24px rgba(0, 0, 0, 0.06), 0 2px 6px rgba(0, 0, 0, 0.03);
}

/* Base Body and App Background */
.stApp {
  background-color: var(--apple-bg) !important;
  font-family: var(--apple-font) !important;
  color: var(--apple-text-primary) !important;
  letter-spacing: -0.01em;
}

/* Hide default streamlit decorations for a native app feel */
#MainMenu, header, footer {
  visibility: hidden;
}

.stMainBlockContainer {
  padding-top: 1.5rem !important;
  padding-bottom: 3.5rem !important;
  max-width: 1360px !important;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
  background-color: #FBFBFD !important;
  border-right: 1px solid var(--apple-border) !important;
}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
  color: var(--apple-text-primary) !important;
  font-weight: 600 !important;
  letter-spacing: -0.015em !important;
}

/* Typography Scale */
h1, .apple-title {
  font-family: var(--apple-font) !important;
  font-size: 28px !important;
  font-weight: 600 !important;
  color: var(--apple-text-primary) !important;
  letter-spacing: -0.025em !important;
  margin-bottom: 4px !important;
}

h2, .apple-section-title {
  font-family: var(--apple-font) !important;
  font-size: 20px !important;
  font-weight: 600 !important;
  color: var(--apple-text-primary) !important;
  letter-spacing: -0.02em !important;
  margin-top: 1.25rem !important;
  margin-bottom: 0.75rem !important;
}

h3, .apple-card-title {
  font-family: var(--apple-font) !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  color: var(--apple-text-primary) !important;
  letter-spacing: -0.01em !important;
}

p, span, label, div {
  font-family: var(--apple-font);
}

/* Bordered Containers as Apple Cards */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--apple-surface) !important;
  border: 1px solid var(--apple-border) !important;
  border-radius: var(--apple-radius-md) !important;
  box-shadow: var(--apple-shadow-card) !important;
  padding: 16px 20px !important;
  margin-bottom: 14px !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05) !important;
}

/* Native Metric Cards Overrides */
[data-testid="stMetric"] {
  background: var(--apple-surface) !important;
  border: 1px solid var(--apple-border) !important;
  border-radius: var(--apple-radius-md) !important;
  padding: 16px 20px !important;
  box-shadow: var(--apple-shadow-card) !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

[data-testid="stMetric"]:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
}

[data-testid="stMetricLabel"] {
  font-size: 12px !important;
  font-weight: 600 !important;
  color: var(--apple-text-secondary) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.03em !important;
  margin-bottom: 4px !important;
}

[data-testid="stMetricValue"] {
  font-size: 28px !important;
  font-weight: 600 !important;
  color: var(--apple-text-primary) !important;
  letter-spacing: -0.03em !important;
}

[data-testid="stMetricDelta"] {
  font-size: 12px !important;
  font-weight: 500 !important;
}

/* Native Button Styling */
.stButton > button {
  background-color: var(--apple-surface) !important;
  color: var(--apple-text-primary) !important;
  border: 1px solid var(--apple-border) !important;
  border-radius: var(--apple-radius-sm) !important;
  font-weight: 500 !important;
  font-size: 14px !important;
  padding: 8px 18px !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
  transition: all 0.15s ease !important;
}

.stButton > button:hover {
  border-color: var(--apple-blue) !important;
  color: var(--apple-blue) !important;
  background-color: var(--apple-surface-hover) !important;
}

.stButton > button:active {
  transform: scale(0.985);
}

/* Primary Action Buttons */
.stButton > button[kind="primary"] {
  background-color: var(--apple-blue) !important;
  color: #FFFFFF !important;
  border: 1px solid var(--apple-blue) !important;
  box-shadow: 0 1px 3px rgba(0, 122, 255, 0.25) !important;
}

.stButton > button[kind="primary"]:hover {
  background-color: #0066D6 !important;
  border-color: #0066D6 !important;
  color: #FFFFFF !important;
}

/* Download Buttons */
.stDownloadButton > button {
  background-color: var(--apple-surface) !important;
  color: var(--apple-blue) !important;
  border: 1px solid var(--apple-blue-border) !important;
  border-radius: var(--apple-radius-sm) !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  padding: 10px 18px !important;
  box-shadow: var(--apple-shadow-card) !important;
  transition: all 0.15s ease !important;
  width: 100% !important;
}

.stDownloadButton > button:hover {
  border-color: var(--apple-blue) !important;
  color: #FFFFFF !important;
  background-color: var(--apple-blue) !important;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.3) !important;
}

/* Form Inputs, Selectboxes, and Multiselects */
[data-baseweb="select"] {
  border-radius: var(--apple-radius-sm) !important;
}

[data-baseweb="select"] > div {
  background-color: var(--apple-surface) !important;
  border: 1px solid var(--apple-border) !important;
  border-radius: var(--apple-radius-sm) !important;
  font-size: 14px !important;
}

/* Dataframe & Tables */
[data-testid="stDataFrame"] {
  background: var(--apple-surface) !important;
  border: 1px solid var(--apple-border) !important;
  border-radius: var(--apple-radius-md) !important;
  overflow: hidden !important;
  box-shadow: var(--apple-shadow-card) !important;
}

/* Expanders */
[data-testid="stExpander"] {
  background: var(--apple-surface) !important;
  border: 1px solid var(--apple-border) !important;
  border-radius: var(--apple-radius-md) !important;
  box-shadow: var(--apple-shadow-card) !important;
  overflow: hidden !important;
  margin-bottom: 1rem !important;
}

[data-testid="stExpander"] summary {
  font-weight: 500 !important;
  font-size: 14px !important;
  color: var(--apple-text-primary) !important;
  padding: 12px 16px !important;
}

/* Custom Badges */
.apple-badge {
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  padding: 3px 9px;
  border-radius: 980px;
  text-transform: uppercase;
}

.apple-badge-blue {
  background-color: var(--apple-blue-soft);
  color: var(--apple-blue);
  border: 1px solid var(--apple-blue-border);
}

.apple-badge-red {
  background-color: var(--apple-red-soft);
  color: var(--apple-red);
  border: 1px solid rgba(215, 0, 21, 0.2);
}

.apple-badge-amber {
  background-color: var(--apple-amber-soft);
  color: var(--apple-amber);
  border: 1px solid rgba(183, 110, 0, 0.2);
}

.apple-badge-green {
  background-color: var(--apple-green-soft);
  color: var(--apple-green);
  border: 1px solid rgba(36, 138, 61, 0.2);
}

.apple-badge-gray {
  background-color: var(--apple-surface-muted);
  color: var(--apple-text-secondary);
  border: 1px solid var(--apple-border);
}

/* Top App Banner */
.apple-header-bar {
  background: var(--apple-surface);
  border: 1px solid var(--apple-border);
  border-radius: var(--apple-radius-lg);
  padding: 18px 24px;
  margin-bottom: 20px;
  box-shadow: var(--apple-shadow-card);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
}

.apple-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.apple-app-icon {
  width: 44px;
  height: 44px;
  border-radius: 11px;
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 22px;
  box-shadow: 0 4px 10px rgba(0, 122, 255, 0.28);
}

.apple-header-title {
  font-size: 21px;
  font-weight: 600;
  color: var(--apple-text-primary);
  letter-spacing: -0.02em;
  margin: 0;
  line-height: 1.2;
}

.apple-header-subtitle {
  font-size: 13px;
  color: var(--apple-text-secondary);
  margin-top: 3px;
}

.apple-header-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* Incident Evidence Callout Card */
.apple-incident-card {
  background: var(--apple-surface);
  border: 1px solid var(--apple-border);
  border-radius: var(--apple-radius-md);
  padding: 16px 20px;
  margin-bottom: 12px;
  box-shadow: var(--apple-shadow-card);
  border-left: 4px solid var(--apple-red);
}

.apple-incident-card.warning {
  border-left-color: var(--apple-amber);
}

.apple-incident-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.apple-quote {
  font-style: italic;
  font-size: 13px;
  color: var(--apple-text-secondary);
  background: var(--apple-surface-muted);
  border-radius: var(--apple-radius-sm);
  padding: 8px 12px;
  margin-top: 8px;
  line-height: 1.45;
}
</style>
"""


def render_header(total_records=0, active_source="Synthetic 40k Benchmark"):
    """Render Apple-styled application header with metadata chips."""
    is_numeric = False
    if isinstance(total_records, (int, float)):
        records_str = f"{int(total_records):,}"
        is_numeric = True
    else:
        try:
            cleaned = str(total_records).replace(",", "").strip()
            records_str = f"{int(float(cleaned)):,}"
            is_numeric = True
        except (ValueError, TypeError):
            records_str = str(total_records) if total_records is not None else "0"

    record_badge = f"{records_str} Records Live" if is_numeric else records_str

    return f"""
    <div class="apple-header-bar">
      <div class="apple-header-left">
        <div class="apple-app-icon">📡</div>
        <div>
          <div class="apple-header-title">VoicePulse AI</div>
          <div class="apple-header-subtitle">Voice-of-Store Operational Engine · Retail R5 Challenge</div>
        </div>
      </div>
      <div class="apple-header-tags">
        <span class="apple-badge apple-badge-blue">Dataset: {active_source}</span>
        <span class="apple-badge apple-badge-green">{record_badge}</span>
        <span class="apple-badge apple-badge-gray">31-Class Taxonomy</span>
        <span class="apple-badge apple-badge-gray">Apple HIG System</span>
      </div>
    </div>
    """


def render_seeded_incident_card(incident_id, store_id, issue_type, owner, pattern, start_day, quotes, alert_level="CRITICAL"):
    """Render an Apple-style incident audit card with metadata and frontline evidence quotes."""
    badge_class = "apple-badge-red" if alert_level == "CRITICAL" else "apple-badge-amber"
    quotes_html = "".join([f'<div class="apple-quote">“{q}”</div>' for q in quotes])
    
    return f"""
    <div class="apple-incident-card {'warning' if alert_level != 'CRITICAL' else ''}">
      <div class="apple-incident-meta">
        <span class="apple-badge {badge_class}">{alert_level} ALERT</span>
        <span style="font-weight: 600; font-size: 14px; color: var(--apple-text-primary);">{incident_id}</span>
        <span class="apple-badge apple-badge-gray">Store {store_id}</span>
        <span class="apple-badge apple-badge-blue">Owner: {owner}</span>
        <span style="font-size: 12px; color: var(--apple-text-secondary); margin-left: auto;">Pattern: {pattern} ({start_day})</span>
      </div>
      <div style="font-size: 13px; font-weight: 500; color: var(--apple-text-primary); margin-top: 6px;">
        Incident Signature: <code>{issue_type}</code>
      </div>
      <div style="margin-top: 8px;">
        <span style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--apple-text-secondary); letter-spacing: 0.03em;">
          Frontline Evidence & Customer Quotes:
        </span>
        {quotes_html}
      </div>
    </div>
    """
