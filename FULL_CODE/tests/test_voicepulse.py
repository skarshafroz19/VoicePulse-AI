import unittest

import pandas as pd
from engine import (
    POLICY_HIGH_SEVERITY_ISSUES,
    VoicePulseClassifier,
    build_regional_weekly_brief,
    deduplicate_same_day,
    detect_emerging_incidents,
    extract_locality,
    normalise_text,
    resolve_store_ids,
)


class TestVoicePulseEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_stores = pd.DataFrame([
            {"store_id": "ST-001JY", "store_name": "Saffron Market Gariahat", "region": "East"},
            {"store_id": "ST-D69EG", "store_name": "Saffron Market Kankarbagh", "region": "East"},
            {"store_id": "ST-KXEU6", "store_name": "Saffron Hyper Kothrud", "region": "West"},
        ])

        cls.sample_taxonomy = pd.DataFrame([
            {"issue_type_id": "IT17", "issue_type": "Foreign object in product", "owner_function": "Merchandising", "policy_severity_floor": "high"},
            {"issue_type_id": "IT01", "issue_type": "Long checkout queue", "owner_function": "Store Ops", "policy_severity_floor": "low"},
            {"issue_type_id": "NI01", "issue_type": "Praise", "owner_function": "None", "policy_severity_floor": "low"},
        ])

        cls.train_df = pd.DataFrame([
            {"feedback_id": "FB-1", "text": "keeda mila rice packet mein", "issue_type_id": "IT17", "severity": "high", "actionable": 1},
            {"feedback_id": "FB-2", "text": "billing queue is very long at checkout", "issue_type_id": "IT01", "severity": "low", "actionable": 1},
            {"feedback_id": "FB-3", "text": "great store helpful staff love shopping", "issue_type_id": "NI01", "severity": "low", "actionable": 0},
            {"feedback_id": "FB-4", "text": "foreign object insect in food item", "issue_type_id": "IT17", "severity": "high", "actionable": 1},
            {"feedback_id": "FB-5", "text": "slow cashier long line counters closed", "issue_type_id": "IT01", "severity": "low", "actionable": 1},
            {"feedback_id": "FB-6", "text": "excellent service clean store", "issue_type_id": "NI01", "severity": "low", "actionable": 0},
        ])
        cls.clf = VoicePulseClassifier().fit(cls.train_df, cls.sample_taxonomy)

    def test_extract_locality(self):
        self.assertEqual(extract_locality("Saffron Market Kothrud"), "Kothrud")
        self.assertEqual(extract_locality("Saffron Hyper Whitefield"), "Whitefield")
        self.assertEqual(extract_locality("Saffron Express Anna Nagar"), "Anna Nagar")

    def test_normalise_text(self):
        text = "Hello!! http://saffronretail.example/order  yaar bahut bheed hai  "
        cleaned = normalise_text(text)
        self.assertIn("yaar bahut bheed hai", cleaned)
        self.assertNotIn("http", cleaned)

    def test_resolve_store_ids(self):
        df = pd.DataFrame([
            {"store_id": "ST-001JY", "text": "good service"},
            {"store_id": None, "text": "billing was slow at kankarbagh branch"},
            {"store_id": None, "text": "app checkout payment failed"},
        ])
        resolved = resolve_store_ids(df, self.sample_stores)
        self.assertEqual(resolved.iloc[0], "ST-001JY")
        self.assertEqual(resolved.iloc[1], "ST-D69EG")
        self.assertIsNone(resolved.iloc[2])

    def test_policy_high_severity_enforcement(self):
        self.assertIn("IT17", POLICY_HIGH_SEVERITY_ISSUES)
        self.assertIn("IT10", POLICY_HIGH_SEVERITY_ISSUES)
        self.assertIn("IT18", POLICY_HIGH_SEVERITY_ISSUES)
        self.assertIn("IT04", POLICY_HIGH_SEVERITY_ISSUES)

    def test_classifier_prediction_and_overrides(self):
        test_df = pd.DataFrame([
            {"feedback_id": "T1", "text": "keeda insect worm in daliya packet"},
            {"feedback_id": "T2", "text": "great store helpful staff love shopping here"},
        ])
        preds = self.clf.predict(test_df)
        self.assertEqual(preds.loc[0, "issue_type_id"], "IT17")
        self.assertEqual(preds.loc[0, "severity"], "high")  # Policy high floor
        self.assertEqual(preds.loc[1, "issue_type_id"], "NI01")
        self.assertEqual(preds.loc[1, "actionable"], 0)  # Non-issue must have 0 actionable

    def test_deduplicate_same_day(self):
        df = pd.DataFrame([
            {"feedback_id": "F1", "store_id": "ST-D69EG", "created_at": "2026-05-04T10:00:00", "text": "freezer warm ice cream melted"},
            {"feedback_id": "F2", "store_id": "ST-D69EG", "created_at": "2026-05-04T12:30:00", "text": "Freezer warm ice cream melted!"},
            {"feedback_id": "F3", "store_id": "ST-D69EG", "created_at": "2026-05-05T10:00:00", "text": "freezer warm ice cream melted"},
        ])
        dedup = deduplicate_same_day(df)
        self.assertFalse(dedup.loc[0, "is_duplicate"])
        self.assertTrue(dedup.loc[1, "is_duplicate"])  # Same store, same day, same normalized text
        self.assertFalse(dedup.loc[2, "is_duplicate"])  # Different day

    def test_emerging_incidents_causal_structure(self):
        # Construct 3 weeks of feedback where week 3 has a surge of IT17 at ST-D69EG
        records = []
        for i in range(10):
            records.append({"feedback_id": f"W1_{i}", "store_id": "ST-D69EG", "issue_type_id": "IT01", "created_at": "2026-04-13T10:00:00", "text": "queue"})
            records.append({"feedback_id": f"W2_{i}", "store_id": "ST-D69EG", "issue_type_id": "IT01", "created_at": "2026-04-20T10:00:00", "text": "queue"})
        # Surge week
        records.append({"feedback_id": "W3_1", "store_id": "ST-D69EG", "issue_type_id": "IT17", "created_at": "2026-04-27T10:00:00", "text": "worm"})
        records.append({"feedback_id": "W3_2", "store_id": "ST-D69EG", "issue_type_id": "IT17", "created_at": "2026-04-27T11:00:00", "text": "insect"})
        records.append({"feedback_id": "W3_3", "store_id": "ST-D69EG", "issue_type_id": "IT17", "created_at": "2026-04-27T12:00:00", "text": "stone"})

        df = pd.DataFrame(records)
        flags = detect_emerging_incidents(df, self.sample_stores, as_of_week_start="2026-04-27")
        self.assertFalse(flags.empty)
        self.assertIn("ST-D69EG", flags["store_id"].values)
        self.assertIn("IT17", flags["issue_type_id"].values)
        self.assertGreaterEqual(flags.iloc[0]["evidence_feedback_ids"].count(";") + 1, 2)

    def test_regional_weekly_brief_generation(self):
        scored_df = pd.DataFrame([
            {"feedback_id": "B1", "store_id": "ST-001JY", "week_start": "2026-05-04", "issue_type_id": "IT01", "severity": "low", "actionable": 1, "text": "long queue at billing counter"},
            {"feedback_id": "B2", "store_id": "ST-D69EG", "week_start": "2026-05-04", "issue_type_id": "IT17", "severity": "high", "actionable": 1, "text": "insect in atta packet"},
        ])
        brief = build_regional_weekly_brief(
            scored_df=scored_df,
            store_master=self.sample_stores,
            taxonomy_df=self.sample_taxonomy,
            region="East",
            week_start="2026-05-04"
        )
        self.assertIn("Regional Weekly Action Brief: EAST REGION", brief)
        self.assertIn("Top 5 Operational Issues", brief)
        self.assertIn("IT17", brief)


if __name__ == "__main__":
    unittest.main()
