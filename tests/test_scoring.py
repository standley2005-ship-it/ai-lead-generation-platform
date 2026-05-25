import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lead_generation.scoring import Lead, score_lead  # noqa: E402


class LeadScoringTests(unittest.TestCase):
    def test_scores_qualified_automation_lead(self):
        lead = Lead(
            lead_id="lead-1",
            business_name="Example Co",
            contact_name="Sample Contact",
            email="sample@example.com",
            service_interest="AI follow-up automation",
            timeline="30 days",
            notes="Needs help responding to inbound leads faster.",
        )

        result = score_lead(lead)

        self.assertEqual(result.status, "qualified")
        self.assertGreaterEqual(result.score, 70)


if __name__ == "__main__":
    unittest.main()

