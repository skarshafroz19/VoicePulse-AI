import os
import sys
import unittest

# Ensure parent directory (FULL_CODE) is available on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
from engine import (
    build_weekly_brief,
    deduplicate_records,
    emerging_incidents,
    evaluate_incident_lead_time,
    load_taxonomy,
    normalise,
    prepare_feedback,
    score_feedback,
)


class TestVoicePulseEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tax = load_taxonomy()

    def test_normalise_text(self):
        # Preserves Hinglish while removing noise
        raw_text = "Urgent: Fridge is warm!! http://example.com/log yaar bahut problem hai"
        cleaned = normalise(raw_text)
        self.assertIn("fridge is warm", cleaned)
        self.assertIn("yaar bahut problem hai", cleaned)
        self.assertNotIn("http", cleaned)
        self.assertNotIn("!!", cleaned)

    def test_taxonomy_completeness(self):
        self.assertGreaterEqual(len(self.tax), 31, "Taxonomy must contain all 31 operational classes")
        self.assertIn("freezer_cold_chain", self.tax)
        self.assertIn("allergen_mislabel", self.tax)
        self.assertIn("positive_feedback", self.tax)
        self.assertIn("workplace_safety", self.tax)

    def test_prepare_feedback_column_aliases(self):
        raw_df = pd.DataFrame([{
            "feedback_id": "TKT-001",
            "branch_id": "ST017",
            "created_at": "2026-09-21 14:04:00",
            "comment": "Freezer is warm and ice cream melted",
            "source": "online_review"
        }])
        prep = prepare_feedback(raw_df)
        self.assertEqual(prep.loc[0, "record_id"], "TKT-001")
        self.assertEqual(prep.loc[0, "store_id"], "ST017")
        self.assertEqual(prep.loc[0, "channel"], "online_review")
        self.assertFalse(prep["date_parsed"].isna().all())
        self.assertIn("week_start", prep.columns)

    def test_prepare_feedback_store_master_join(self):
        raw_df = pd.DataFrame([{
            "record_id": "R1",
            "store_id": "ST017",
            "date": "2026-09-21",
            "text": "Store issues"
        }])
        store_master = pd.DataFrame([{
            "store_id": "ST017",
            "store_name": "South Market 017",
            "region": "South",
            "store_size": "Small",
            "avg_weekly_transactions": 1528
        }])
        prep = prepare_feedback(raw_df, store_master=store_master)
        self.assertEqual(prep.loc[0, "region"], "South")
        self.assertEqual(prep.loc[0, "transactions"], 1528)

    def test_classification_and_policy_overrides(self):
        samples = pd.DataFrame([
            {"record_id": "1", "store_id": "S1", "date": "2026-09-21", "text": "allergen label is wrong, contains peanut but says no nuts"},
            {"record_id": "2", "store_id": "S1", "date": "2026-09-21", "text": "staff member was rude and cashier shouted at customer"},
            {"record_id": "3", "store_id": "S1", "date": "2026-09-21", "text": "spill caused slip hazard in aisle, blocked emergency exit"},
            {"record_id": "4", "store_id": "S1", "date": "2026-09-21", "text": "Staff were helpful and the store was clean 🙂"},
            {"record_id": "5", "store_id": "S1", "date": "2026-09-21", "text": "Billing counter error, charged twice on credit card"}
        ])
        prep = prepare_feedback(samples)
        scored = score_feedback(prep, taxonomy=self.tax)

        # 1. Allergen Mislabel -> HIGH severity, Store Ops
        self.assertEqual(scored.loc[0, "issue_type"], "allergen_mislabel")
        self.assertEqual(scored.loc[0, "severity"], "HIGH")
        self.assertEqual(scored.loc[0, "owner"], "Store Ops")
        self.assertTrue(scored.loc[0, "actionable"])

        # 2. Staff Misconduct -> HIGH severity, HR
        self.assertEqual(scored.loc[1, "issue_type"], "staff_misconduct")
        self.assertEqual(scored.loc[1, "severity"], "HIGH")
        self.assertEqual(scored.loc[1, "owner"], "HR")

        # 3. Workplace Safety -> HIGH severity, HR
        self.assertEqual(scored.loc[2, "issue_type"], "workplace_safety")
        self.assertEqual(scored.loc[2, "severity"], "HIGH")
        self.assertEqual(scored.loc[2, "owner"], "HR")

        # 4. Positive Feedback -> LOW severity, actionable False
        self.assertEqual(scored.loc[3, "issue_type"], "positive_feedback")
        self.assertEqual(scored.loc[3, "severity"], "LOW")
        self.assertFalse(scored.loc[3, "actionable"])

        # 5. Billing Error -> Store Ops
        self.assertEqual(scored.loc[4, "issue_type"], "billing_error")
        self.assertEqual(scored.loc[4, "owner"], "Store Ops")
        self.assertTrue(scored.loc[4, "actionable"])

    def test_conservative_deduplication(self):
        # Same store + same day with near-identical core phrase should cluster
        records = pd.DataFrame([
            {"record_id": "R1", "store_id": "ST017", "date": "2026-10-13 10:00:00", "text": "allergen label is wrong on snack pack"},
            {"record_id": "R2", "store_id": "ST017", "date": "2026-10-13 14:00:00", "text": "Today allergen label is wrong on snack pack 😤"},
            {"record_id": "R3", "store_id": "ST017", "date": "2026-10-13 18:00:00", "text": "FYI allergen label is wrong on snack pack yaar bahut problem hai"},
            {"record_id": "R4", "store_id": "ST018", "date": "2026-10-13 10:00:00", "text": "allergen label is wrong on snack pack"}, # Different store
            {"record_id": "R5", "store_id": "ST017", "date": "2026-10-14 10:00:00", "text": "allergen label is wrong on snack pack"}  # Different day
        ])
        prep = prepare_feedback(records)
        deduped = deduplicate_records(prep)

        # R1, R2, R3 must share the same duplicate_group
        grp1 = deduped.loc[0, "duplicate_group"]
        grp2 = deduped.loc[1, "duplicate_group"]
        grp3 = deduped.loc[2, "duplicate_group"]
        self.assertEqual(grp1, grp2)
        self.assertEqual(grp1, grp3)
        self.assertFalse(deduped.loc[0, "is_duplicate"], "First record should be primary")
        self.assertTrue(deduped.loc[1, "is_duplicate"])
        self.assertTrue(deduped.loc[2, "is_duplicate"])

        # Different store and different day must have different groups
        self.assertNotEqual(grp1, deduped.loc[3, "duplicate_group"])
        self.assertNotEqual(grp1, deduped.loc[4, "duplicate_group"])

    def test_emerging_incidents_radar_surge(self):
        # Create a time series with baseline=0 for weeks 1-3, surge=4 in week 4
        weeks = pd.date_range("2026-09-01", periods=4, freq="W-MON")
        rows = []
        for w in weeks[:3]:
            rows.append({"store_id": "ST099", "date": str(w), "text": "Routine check", "issue_type": "freezer_cold_chain", "transactions": 1000})
        # Surge week
        for _ in range(5):
            rows.append({"store_id": "ST099", "date": str(weeks[3]), "text": "freezer not cooling ice cream melted", "issue_type": "freezer_cold_chain", "transactions": 1000})

        df = pd.DataFrame(rows)
        prep = prepare_feedback(df)
        prep["severity"] = "HIGH"
        radar = emerging_incidents(prep)

        self.assertFalse(radar.empty, "Radar must detect 5x freezer surge")
        st99_alert = radar[radar["store_id"] == "ST099"]
        self.assertFalse(st99_alert.empty)
        self.assertGreaterEqual(float(st99_alert.iloc[0]["growth_ratio"]), 2.0)
        self.assertEqual(st99_alert.iloc[0]["alert_level"], "CRITICAL")

    def test_regional_weekly_brief(self):
        data = pd.DataFrame([
            {"record_id": "1", "store_id": "S1", "region": "North", "date": "2026-09-21", "text": "dirty floor cockroach seen", "issue_type": "hygiene_pest", "owner": "Store Ops", "severity": "HIGH", "actionable": True},
            {"record_id": "2", "store_id": "S2", "region": "North", "date": "2026-09-21", "text": "Staff were helpful and store clean", "issue_type": "positive_feedback", "owner": None, "severity": "LOW", "actionable": False}
        ])
        brief = build_weekly_brief(data, region="North")
        self.assertIn("North", brief)
        self.assertIn("Total Records Reviewed", brief)
        self.assertIn("Hygiene Pest", brief)
        self.assertIn("Store Ops", brief)

    def test_incident_lead_time_evaluation(self):
        radar_df = pd.DataFrame([{
            "store_id": "ST017",
            "issue_type": "freezer_cold_chain",
            "week_start": "2026-09-21",
            "alert_level": "CRITICAL",
            "growth_ratio": 4.5,
            "count": 4
        }])
        manifest_df = pd.DataFrame([{
            "incident_id": "SYNTH_INCIDENT_1",
            "store_id": "ST017",
            "issue_type": "freezer_cold_chain",
            "start_day": 77,
            "pattern": "gradual"
        }])
        feedback_df = pd.DataFrame([{"date": "2026-07-01"}])
        lt = evaluate_incident_lead_time(radar_df, manifest_df, feedback_df)

        self.assertEqual(len(lt), 1)
        self.assertEqual(lt.loc[0, "status"], "DETECTED")
        self.assertGreater(lt.loc[0, "lead_time_vs_monthly_days"], 20.0)

    def test_empty_and_corrupt_input_resilience(self):
        empty_df = pd.DataFrame()
        prep = prepare_feedback(empty_df)
        self.assertTrue(prep.empty)
        scored = score_feedback(prep)
        self.assertTrue(scored.empty)
        radar = emerging_incidents(scored)
        self.assertTrue(radar.empty)

        # Corrupt data
        corrupt_df = pd.DataFrame([
            {"record_id": None, "store_id": None, "date": "not-a-date", "text": None}
        ])
        prep_c = prepare_feedback(corrupt_df)
        scored_c = score_feedback(prep_c)
        self.assertEqual(len(scored_c), 1)
        self.assertEqual(scored_c.loc[0, "store_id"], "UNKNOWN")

if __name__ == "__main__":
    unittest.main()
