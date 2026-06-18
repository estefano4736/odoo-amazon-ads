import unittest
import sys
import os

# Include project base directory in search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.rules import calculate_smart_bid, identify_negatives, redistribute_budgets

class TestRulesEngine(unittest.TestCase):

    def test_smart_bid_decrease_high_acos(self):
        """Bids should decrease if current ACOS is higher than Target ACOS."""
        # Target ACOS: 30%, Current ACOS: 40% (Spend: 40.0, Sales: 100.0)
        res = calculate_smart_bid(
            current_bid=2.50,
            clicks=20,
            spend=40.0,
            sales=100.0,
            orders=5,
            target_acos=0.30,
            min_bid=0.02,
            max_bid=5.00,
            smoothing_factor=0.3
        )
        self.assertEqual(res["action"], "DECREASE")
        self.assertLess(res["new_bid"], 2.50)
        self.assertTrue("above Target" in res["reason"])

    def test_smart_bid_increase_low_acos(self):
        """Bids should increase or adjust if current ACOS is lower than Target ACOS (profitable)."""
        # Target ACOS: 30%, Current ACOS: 15% (Spend: 15.0, Sales: 100.0)
        # Bid = 1.00. Target Bid calculation: CR (5/20=0.25) * AOV (100/5=20) * 0.3 = 1.50
        # New Bid = 1.0 * 0.7 + 1.5 * 0.3 = 1.15
        res = calculate_smart_bid(
            current_bid=1.00,
            clicks=20,
            spend=15.0,
            sales=100.0,
            orders=5,
            target_acos=0.30,
            min_bid=0.02,
            max_bid=5.00,
            smoothing_factor=0.3
        )
        self.assertEqual(res["action"], "INCREASE")
        self.assertEqual(res["new_bid"], 1.15)
        self.assertTrue("profitable" in res["reason"])

    def test_smart_bid_no_sales(self):
        """Bids should reduce by 20% if there are clicks but zero sales."""
        res = calculate_smart_bid(
            current_bid=1.00,
            clicks=12,
            spend=15.0,
            sales=0.0,
            orders=0,
            target_acos=0.30,
            min_bid=0.02,
            max_bid=5.00,
            smoothing_factor=0.3
        )
        self.assertEqual(res["action"], "DECREASE")
        self.assertEqual(res["new_bid"], 0.80)
        self.assertTrue("0 sales" in res["reason"])

    def test_smart_bid_min_max_bounds(self):
        """Calculated bids must stay within min_bid and max_bid boundaries."""
        # High performer suggesting $6.00 bid, but max_bid is $3.00
        res = calculate_smart_bid(
            current_bid=2.50,
            clicks=10,
            spend=5.0,
            sales=200.0,
            orders=5,
            target_acos=0.30,
            min_bid=0.05,
            max_bid=3.00,
            smoothing_factor=1.0 # Force instant adjustment to calculated target
        )
        self.assertEqual(res["new_bid"], 3.00)

    def test_identify_negatives_spend_limit(self):
        """Search terms with spend exceeding max_spend and zero sales should be negativized."""
        terms = [
            {"customer_search_term": "bad keyword term", "clicks": 15, "spend": 18.50, "sales": 0.0, "orders": 0},
            {"customer_search_term": "good keyword term", "clicks": 5, "spend": 4.50, "sales": 50.0, "orders": 1}
        ]
        res = identify_negatives(terms, max_spend_no_sales=15.0, min_clicks_no_sales=10)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["keyword_text"], "bad keyword term")
        self.assertEqual(res[0]["recommendation_type"], "NEGATIVIZATION")
        self.assertTrue("spend" in res[0]["reason"].lower())

    def test_identify_negatives_clicks_limit(self):
        """Search terms with clicks exceeding limit and zero sales should be negativized."""
        terms = [
            {"customer_search_term": "high click no sales", "clicks": 12, "spend": 9.00, "sales": 0.0, "orders": 0}
        ]
        # max_spend is $15, but click limit is 10
        res = identify_negatives(terms, max_spend_no_sales=15.0, min_clicks_no_sales=10)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["keyword_text"], "high click no sales")
        self.assertTrue("clicks" in res[0]["reason"].lower())

    def test_budget_redistribution(self):
        """Budgets should shift from underperforming to high-performing campaigns hitting limits."""
        campaigns = [
            # High performing: spend ratio 96%, ACOS 15% (under target 30%), needs cash
            {"campaign_name": "Camp Alpha", "budget": 50.0, "spend": 48.0, "sales": 320.0, "orders": 15},
            # Underperforming: spend ratio 20%, ACOS 60% (above target 30%), has excess
            {"campaign_name": "Camp Beta", "budget": 100.0, "spend": 20.0, "sales": 33.3, "orders": 1}
        ]
        # Beta leftover: $80. Transfer 15% ($12.00) from Beta to Alpha
        res = redistribute_budgets(campaigns, target_acos=0.30, budget_transfer_pct=0.15)
        self.assertEqual(len(res), 2)
        
        # Verify recommendation fields
        hp_recom = [r for r in res if r["campaign_name"] == "Camp Alpha"][0]
        self.assertEqual(hp_recom["recommended_value"], 62.00) # 50 + 12
        self.assertTrue("highly profitable" in hp_recom["reason"].lower())
        
        up_recom = [r for r in res if r["campaign_name"] == "Camp Beta"][0]
        self.assertEqual(up_recom["recommended_value"], 88.00) # 100 - 12
        self.assertTrue("underperforming" in up_recom["reason"].lower())

if __name__ == "__main__":
    unittest.main()
