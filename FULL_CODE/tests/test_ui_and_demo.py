import unittest
import pandas as pd
from engine import VoicePulseClassifier
from styles import render_header, render_jury_banner, render_section_banner, render_empty_state


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


if __name__ == "__main__":
    unittest.main()
