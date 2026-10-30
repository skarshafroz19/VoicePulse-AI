import unittest
import pandas as pd
from engine import VoicePulseClassifier, build_regional_weekly_brief
from styles import (
    render_header,
    render_jury_banner,
    render_section_banner,
    render_empty_state,
    render_dashboard_preview,
    render_navbar,
    render_return_banner,
    render_footer,
)


class TestUIAndDemo(unittest.TestCase):
    def test_render_header_defensive_formatting(self):
        # Numeric int
        h1 = render_header(39769, "Official Stream")
        self.assertIn("39,769 Records Live", h1)
        self.assertIn("Dataset: Official Stream", h1)

        # Numeric str
        h2 = render_header("39,769", "Official Stream")
        self.assertIn("39,769 Records Live", h2)

        # String section title
        h3 = render_header("Executive Operational Overview", "Subtitle")
        self.assertIn("Executive Operational Overview", h3)

        # Zero and None
        h4 = render_header(0)
        self.assertIn("0 Records Live", h4)
        h5 = render_header(None)
        self.assertIn(">0<", h5)

    def test_render_jury_banner_and_sections(self):
        banner = render_jury_banner(current_step=3, total_steps=6, step_name="Live AI Inference", description="Testing live model")
        self.assertIn("Stage 3 of 6: Live AI Inference", banner)
        self.assertIn("apple-step-pill active", banner)

        sec = render_section_banner(title="Data Explorer", subtitle="Explore records", badge_text="Active", badge_color="green")
        self.assertIn("Data Explorer", sec)
        self.assertIn("apple-badge-green", sec)

        empty = render_empty_state("No Match", "Try again", "🔍")
        self.assertIn("No Match", empty)

    def test_render_dashboard_preview(self):
        preview = render_dashboard_preview()
        self.assertIn("apple-mockup-frame", preview)
        self.assertIn("39,769", preview)
        self.assertIn("+2 Wks Early Lead", preview)

    def test_render_navbar_return_and_footer(self):
        nav = render_navbar("Product Overview")
        self.assertIn("VoicePulse AI", nav)
        self.assertIn("Enterprise SaaS", nav)

        ret = render_return_banner("Executive Operational Overview")
        self.assertIn("Executive Operational Overview", ret)
        self.assertIn("Product Overview", ret)

        ft = render_footer()
        self.assertIn("VoicePulse AI", ft)
        self.assertIn("0.8641", ft)

    def test_classifier_predict_detailed(self):
        clf = VoicePulseClassifier()
        train_df = pd.DataFrame([
            {"feedback_id": "T1", "text": "billing queue delay", "issue_type_id": "IT01", "severity": "low", "actionable": 1},
            {"feedback_id": "T2", "text": "worms insect contamination in rice", "issue_type_id": "IT17", "severity": "high", "actionable": 1},
            {"feedback_id": "T3", "text": "freezer chiller broken ice cream melted", "issue_type_id": "IT10", "severity": "high", "actionable": 1},
            {"feedback_id": "T4", "text": "great clean store friendly staff", "issue_type_id": "NI01", "severity": "low", "actionable": 0},
        ])
        clf.fit(train_df)

        test_df = pd.DataFrame([{"text": "Found bugs in rice packet"}])
        pred = clf.predict_detailed(test_df)
        self.assertIn("issue_confidence", pred.columns)
        self.assertIn("severity_confidence", pred.columns)
        self.assertIn("actionable_confidence", pred.columns)
        self.assertIn("policy_override_applied", pred.columns)
        self.assertGreaterEqual(pred["issue_confidence"].iloc[0], 0.0)
        self.assertLessEqual(pred["issue_confidence"].iloc[0], 1.0)

    def test_build_regional_brief_defensive(self):
        tax_df = pd.DataFrame([
            {"issue_type_id": "IT01", "issue_type": "Billing Queue", "owner_function": "Store Ops"}
        ])
        store_df = pd.DataFrame([
            {"store_id": "ST-001", "store_name": "Kothrud Store", "region": "West"}
        ])

        # 1. Normal case
        scored_df = pd.DataFrame([
            {"feedback_id": "F1", "store_id": "ST-001", "resolved_store_id": "ST-001", "issue_type_id": "IT01", "severity": "low", "actionable": 1, "week_start": "2026-05-04", "text": "queue delay"}
        ])
        brief = build_regional_weekly_brief(scored_df, store_df, tax_df, "West", "2026-05-04")
        self.assertIn("Regional Weekly Action Brief: WEST REGION", brief)
        self.assertIn("Billing Queue", brief)

        # 2. Empty case
        empty_scored = pd.DataFrame(columns=["feedback_id", "store_id", "resolved_store_id", "issue_type_id", "severity", "actionable", "week_start", "text"])
        empty_brief = build_regional_weekly_brief(empty_scored, store_df, tax_df, "West", "2026-05-04")
        self.assertIn("Regional Weekly Action Brief: WEST REGION", empty_brief)
        self.assertIn("Total Feedback:** 0", empty_brief)
        self.assertIn("No actionable issue trends recorded", empty_brief)


if __name__ == "__main__":
    unittest.main()
