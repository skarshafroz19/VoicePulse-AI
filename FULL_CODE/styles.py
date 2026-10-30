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
  --apple-blue: #0071E3;
  --apple-blue-hover: #0056B3;
  --apple-blue-soft: rgba(0, 113, 227, 0.08);
  --apple-blue-border: rgba(0, 113, 227, 0.22);
  --apple-indigo: #5856D6;
  --apple-indigo-soft: rgba(88, 86, 214, 0.08);
  --apple-green: #34C759;
  --apple-green-soft: rgba(52, 199, 89, 0.1);
  --apple-amber: #FF9500;
  --apple-amber-soft: rgba(255, 149, 0, 0.1);
  --apple-red: #FF3B30;
  --apple-red-soft: rgba(255, 59, 48, 0.1);
  --apple-font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --apple-radius-sm: 8px;
  --apple-radius-md: 12px;
  --apple-radius-lg: 16px;
  --apple-radius-pill: 980px;
  --apple-shadow-card: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
  --apple-shadow-hover: 0 6px 18px rgba(0, 0, 0, 0.06), 0 2px 4px rgba(0, 0, 0, 0.03);
  --apple-shadow-float: 0 12px 32px rgba(0, 0, 0, 0.08), 0 2px 6px rgba(0, 0, 0, 0.03);
}

/* Accessibility: Respect Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
    transform: none !important;
  }
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
  padding-top: 1.25rem !important;
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
  padding: 18px 22px !important;
  margin-bottom: 14px !important;
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease !important;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
  box-shadow: var(--apple-shadow-hover) !important;
  transform: translateY(-1px);
}

/* Native Metric Cards Overrides */
[data-testid="stMetric"] {
  background: var(--apple-surface) !important;
  border: 1px solid var(--apple-border) !important;
  border-radius: var(--apple-radius-md) !important;
  padding: 16px 20px !important;
  box-shadow: var(--apple-shadow-card) !important;
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease !important;
}

[data-testid="stMetric"]:hover {
  box-shadow: var(--apple-shadow-hover) !important;
  transform: translateY(-1px);
}

[data-testid="stMetricLabel"] {
  font-size: 11px !important;
  font-weight: 600 !important;
  color: var(--apple-text-secondary) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.04em !important;
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
  box-shadow: 0 1px 3px rgba(0, 113, 227, 0.25) !important;
  font-weight: 600 !important;
}

.stButton > button[kind="primary"]:hover {
  background-color: var(--apple-blue-hover) !important;
  border-color: var(--apple-blue-hover) !important;
  color: #FFFFFF !important;
  box-shadow: 0 3px 8px rgba(0, 113, 227, 0.32) !important;
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
  box-shadow: 0 2px 8px rgba(0, 113, 227, 0.3) !important;
}

/* Form Inputs, Selectboxes, and Text Areas */
[data-baseweb="select"] {
  border-radius: var(--apple-radius-sm) !important;
}

[data-baseweb="select"] > div {
  background-color: var(--apple-surface) !important;
  border: 1px solid var(--apple-border) !important;
  border-radius: var(--apple-radius-sm) !important;
  font-size: 14px !important;
}

.stTextInput input, .stTextArea textarea {
  border-radius: var(--apple-radius-sm) !important;
  border: 1px solid var(--apple-border) !important;
  background-color: var(--apple-surface) !important;
  color: var(--apple-text-primary) !important;
  font-size: 14px !important;
  padding: 10px 12px !important;
  transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--apple-blue) !important;
  box-shadow: 0 0 0 3px var(--apple-blue-soft) !important;
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
  padding: 4px 10px;
  border-radius: var(--apple-radius-pill);
  text-transform: uppercase;
  white-space: nowrap;
}

.apple-badge-blue {
  background-color: var(--apple-blue-soft);
  color: var(--apple-blue);
  border: 1px solid var(--apple-blue-border);
}

.apple-badge-red {
  background-color: var(--apple-red-soft);
  color: var(--apple-red);
  border: 1px solid rgba(255, 59, 48, 0.22);
}

.apple-badge-amber {
  background-color: var(--apple-amber-soft);
  color: var(--apple-amber);
  border: 1px solid rgba(255, 149, 0, 0.22);
}

.apple-badge-green {
  background-color: var(--apple-green-soft);
  color: var(--apple-green);
  border: 1px solid rgba(52, 199, 89, 0.22);
}

.apple-badge-gray {
  background-color: var(--apple-surface-muted);
  color: var(--apple-text-secondary);
  border: 1px solid var(--apple-border);
}

.apple-badge-purple {
  background-color: var(--apple-indigo-soft);
  color: var(--apple-indigo);
  border: 1px solid rgba(88, 86, 214, 0.22);
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
  background: linear-gradient(135deg, #0071E3 0%, #5856D6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 22px;
  box-shadow: 0 4px 10px rgba(0, 113, 227, 0.28);
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

/* Section Header Bar */
.apple-section-banner {
  background: var(--apple-surface);
  border: 1px solid var(--apple-border);
  border-radius: var(--apple-radius-md);
  padding: 14px 20px;
  margin-bottom: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--apple-shadow-card);
}

/* Jury Demo Navigator */
.apple-jury-banner {
  background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FE 100%);
  border: 1px solid rgba(0, 113, 227, 0.25);
  border-radius: var(--apple-radius-lg);
  padding: 16px 22px;
  margin-bottom: 22px;
  box-shadow: 0 4px 16px rgba(0, 113, 227, 0.08);
}

.apple-jury-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.apple-jury-steps {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.apple-step-pill {
  padding: 6px 12px;
  border-radius: var(--apple-radius-pill);
  font-size: 12px;
  font-weight: 500;
  color: var(--apple-text-secondary);
  background: var(--apple-surface-muted);
  border: 1px solid var(--apple-border);
  white-space: nowrap;
}

.apple-step-pill.active {
  color: #FFFFFF;
  background: var(--apple-blue);
  border-color: var(--apple-blue);
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(0, 113, 227, 0.28);
}

.apple-step-pill.completed {
  color: var(--apple-green);
  background: var(--apple-green-soft);
  border-color: rgba(52, 199, 89, 0.25);
  font-weight: 600;
}

/* Live AI Inference Result Card */
.apple-inference-card {
  background: var(--apple-surface);
  border: 1px solid var(--apple-border);
  border-radius: var(--apple-radius-lg);
  padding: 22px 24px;
  box-shadow: var(--apple-shadow-card);
  margin-top: 14px;
}

.apple-confidence-meter {
  height: 6px;
  border-radius: 3px;
  background: var(--apple-surface-muted);
  overflow: hidden;
  margin-top: 6px;
}

.apple-confidence-bar {
  height: 100%;
  border-radius: 3px;
  background: var(--apple-blue);
  transition: width 0.3s ease;
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
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.apple-incident-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--apple-shadow-hover);
}

.apple-incident-card.warning {
  border-left-color: var(--apple-amber);
}

.apple-incident-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  flex-wrap: wrap;
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

/* Empty State */
.apple-empty-state {
  text-align: center;
  padding: 42px 20px;
  background: var(--apple-surface);
  border: 1px dashed var(--apple-border);
  border-radius: var(--apple-radius-md);
  margin: 16px 0;
}

.apple-callout {
  background: var(--apple-surface-muted);
  border-left: 4px solid var(--apple-blue);
  border-radius: 0 var(--apple-radius-sm) var(--apple-radius-sm) 0;
  padding: 14px 18px;
  margin: 14px 0;
  font-size: 13px;
  line-height: 1.5;
  color: var(--apple-text-primary);
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


def render_section_banner(title: str, subtitle: str, badge_text: str | None = None, badge_color: str = "blue") -> str:
    """Render a clean Apple-style section header banner with optional badge."""
    badge_html = f'<span class="apple-badge apple-badge-{badge_color}">{badge_text}</span>' if badge_text else ""
    return f"""
    <div class="apple-section-banner">
      <div>
        <div style="font-size: 17px; font-weight: 600; color: var(--apple-text-primary); letter-spacing: -0.015em;">
          {title}
        </div>
        <div style="font-size: 12px; color: var(--apple-text-secondary); margin-top: 2px;">
          {subtitle}
        </div>
      </div>
      {badge_html}
    </div>
    """


def render_jury_banner(current_step: int, total_steps: int = 6, step_name: str = "", description: str = "") -> str:
    """Render a sticky guided Jury Demonstration stepper bar."""
    step_titles = [
        "1. Problem & Context",
        "2. Stream Pipeline",
        "3. Live AI Inference",
        "4. Emerging Radar",
        "5. Benchmarks",
        "6. Practical Impact"
    ]
    pills_html = []
    for i, title in enumerate(step_titles, start=1):
        if i == current_step:
            cls = "apple-step-pill active"
        elif i < current_step:
            cls = "apple-step-pill completed"
        else:
            cls = "apple-step-pill"
        pills_html.append(f'<span class="{cls}">{title}</span>')

    pills_str = "".join(pills_html)

    return f"""
    <div class="apple-jury-banner">
      <div class="apple-jury-header">
        <div style="display: flex; align-items: center; gap: 10px;">
          <span class="apple-badge apple-badge-blue" style="font-weight: 700;">Jury Demo Mode</span>
          <span style="font-size: 15px; font-weight: 600; color: var(--apple-text-primary);">Stage {current_step} of {total_steps}: {step_name}</span>
        </div>
        <div style="font-size: 12px; color: var(--apple-text-secondary);">Interactive Evaluator Walkthrough</div>
      </div>
      <div style="font-size: 13px; color: var(--apple-text-secondary); margin-bottom: 12px;">{description}</div>
      <div class="apple-jury-steps">
        {pills_str}
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


def render_empty_state(title: str = "No Records Found", message: str = "Try adjusting your search criteria or active filters.", icon: str = "🔍") -> str:
    """Render an Apple-style subtle empty state."""
    return f"""
    <div class="apple-empty-state">
      <div style="font-size: 32px; margin-bottom: 8px;">{icon}</div>
      <div style="font-size: 15px; font-weight: 600; color: var(--apple-text-primary);">{title}</div>
      <div style="font-size: 13px; color: var(--apple-text-secondary); margin-top: 4px; max-width: 400px; margin-left: auto; margin-right: auto;">
        {message}
      </div>
    </div>
    """
