import pandas as pd
from typing import List, Dict, Any

def calculate_smart_bid(
    current_bid: float,
    clicks: int,
    spend: float,
    sales: float,
    orders: int,
    target_acos: float,
    min_bid: float = 0.02,
    max_bid: float = 5.00,
    smoothing_factor: float = 0.3
) -> Dict[str, Any]:
    """
    Calculates the optimized bid for a keyword based on performance metrics and Target ACOS.
    Formula:
      Target Bid = (Orders / Clicks) * (Sales / Orders) * Target ACOS
                 = (Sales / Clicks) * Target ACOS
      
      New Bid = Current Bid * (1 - Alpha) + Target Bid * Alpha
    """
    # Defensive programming
    if current_bid is None or current_bid <= 0:
        current_bid = 0.50  # default starting bid

    # Case 1: Active sales (Optimize toward Target ACOS)
    if clicks > 0 and orders > 0 and sales > 0:
        conversion_rate = orders / clicks
        aov = sales / orders  # Average Order Value
        
        # Calculate target bid
        target_bid = conversion_rate * aov * target_acos
        
        # Apply smoothing
        new_bid = (current_bid * (1 - smoothing_factor)) + (target_bid * smoothing_factor)
        
        # Calculate current ACOS
        acos = spend / sales
        
        # Determine reasoning text
        if acos > target_acos:
            action = "DECREASE"
            reason = f"ACOS ({acos:.1%}) is above Target ({target_acos:.1%}). Reducing bid to control ACOS."
        else:
            action = "INCREASE" if new_bid > current_bid else "HOLD"
            reason = f"ACOS ({acos:.1%}) is profitable (<= Target {target_acos:.1%}). Adjusting bid to maximize visibility."
            
    # Case 2: Clicks but zero sales (Reduce waste)
    elif clicks > 0 and orders == 0:
        # Simple reduction by 20%
        new_bid = current_bid * 0.80
        action = "DECREASE"
        reason = f"Keyword has {clicks} clicks and 0 sales. Reducing bid by 20% to cut wasted spend."
        
    # Case 3: Zero clicks (Low visibility / untested)
    else:
        # Keep bid stable or increase slightly if we suspect it needs testing
        new_bid = current_bid
        action = "HOLD"
        reason = "No click data available. Keeping bid at baseline."

    # Enforce minimum and maximum bounds
    new_bid = max(min_bid, min(max_bid, new_bid))
    # Round to 2 decimals for currency
    new_bid = round(new_bid, 2)
    
    # Check if there is an actual change
    if abs(new_bid - current_bid) < 0.01:
        action = "HOLD"
        reason = "Calculated bid is identical or extremely close to current bid. Holding bid."

    return {
        "new_bid": new_bid,
        "action": action,
        "reason": reason,
        "metrics": {
            "clicks": clicks,
            "spend": spend,
            "sales": sales,
            "orders": orders,
            "acos": (spend / sales) if sales > 0 else 0.0
        }
    }


def identify_negatives(
    search_terms: List[Dict[str, Any]],
    max_spend_no_sales: float,
    min_clicks_no_sales: int
) -> List[Dict[str, Any]]:
    """
    Scans search term rows and flags terms that have high spend or clicks but no conversions.
    """
    negatives = []
    for term in search_terms:
        clicks = int(term.get("clicks", 0))
        spend = float(term.get("spend", 0.0))
        sales = float(term.get("sales", 0.0))
        orders = int(term.get("orders", 0))
        term_text = term.get("search_term") or term.get("customer_search_term")
        
        if not term_text:
            continue
            
        # Check rule conditions: 0 orders/sales, and (spend > max_spend OR clicks > min_clicks)
        if orders == 0 and sales == 0 and clicks > 0:
            should_negative = False
            reason = ""
            
            if spend >= max_spend_no_sales:
                should_negative = True
                reason = f"Unproductive spend: Spent ${spend:.2f} with 0 conversions (Threshold: ${max_spend_no_sales:.2f})."
            elif clicks >= min_clicks_no_sales:
                should_negative = True
                reason = f"High click count: {clicks} clicks with 0 conversions (Threshold: {min_clicks_no_sales} clicks)."
                
            if should_negative:
                negatives.append({
                    "entity_type": "SearchTerm",
                    "campaign_name": term.get("campaign_name", "Unknown Campaign"),
                    "ad_group_name": term.get("ad_group_name", "Unknown Ad Group"),
                    "keyword_text": term_text,
                    "match_type": "Negative Exact",
                    "current_value": 0.0,
                    "recommended_value": 0.0,
                    "recommendation_type": "NEGATIVIZATION",
                    "reason": reason,
                    "source": term.get("source", "Report"),
                    "metrics": {
                        "clicks": clicks,
                        "spend": spend,
                        "sales": sales,
                        "orders": orders,
                        "acos": 0.0
                    }
                })
    return negatives


def redistribute_budgets(
    campaigns: List[Dict[str, Any]],
    target_acos: float,
    budget_transfer_pct: float = 0.15
) -> List[Dict[str, Any]]:
    """
    Scans campaign metrics and flags budget reallocation opportunities:
    1. Identify high performing campaigns (ACOS <= Target ACOS) running out of budget (Spend > 90% of Budget).
    2. Identify underperforming campaigns (ACOS > Target ACOS or Sales == 0) with excess budget.
    3. Reallocate budget from the latter to the former.
    """
    high_performers = []
    under_performers = []
    
    for camp in campaigns:
        campaign_name = camp.get("campaign_name")
        budget = float(camp.get("budget", 0.0))
        spend = float(camp.get("spend", 0.0))
        sales = float(camp.get("sales", 0.0))
        orders = int(camp.get("orders", 0))
        
        if budget <= 0:
            continue
            
        acos = (spend / sales) if sales > 0 else 0.0
        spend_ratio = spend / budget
        
        # High performers: converting, profitable ACOS, and capping budget
        if orders > 0 and sales > 0 and acos <= target_acos and spend_ratio >= 0.90:
            high_performers.append({
                "campaign_name": campaign_name,
                "budget": budget,
                "spend": spend,
                "sales": sales,
                "acos": acos,
                "spend_ratio": spend_ratio,
                "leftover": budget - spend
            })
            
        # Under performers: spent money, bad ACOS, or no sales, with leftover budget
        elif (acos > target_acos or (spend > 5.0 and orders == 0)) and spend_ratio < 0.60:
            under_performers.append({
                "campaign_name": campaign_name,
                "budget": budget,
                "spend": spend,
                "sales": sales,
                "acos": acos,
                "spend_ratio": spend_ratio,
                "leftover": budget - spend
            })

    recommendations = []
    
    # If we have both high performers needing budget and underperformers with leftover
    if high_performers and under_performers:
        # Sort underperformers by how much leftover they have
        under_performers.sort(key=lambda x: x["leftover"], reverse=True)
        # Sort high performers by ACOS (best first)
        high_performers.sort(key=lambda x: x["acos"])
        
        # Redistribute
        for hp in high_performers:
            if not under_performers:
                break
                
            # Take the largest underperformer
            up = under_performers[0]
            transfer_amount = round(up["leftover"] * budget_transfer_pct, 2)
            
            if transfer_amount >= 1.0: # Only bother with transfer >= $1.00
                new_hp_budget = hp["budget"] + transfer_amount
                new_up_budget = up["budget"] - transfer_amount
                
                # Check if we should recommend
                recommendations.append({
                    "entity_type": "Campaign",
                    "campaign_name": hp["campaign_name"],
                    "ad_group_name": "N/A",
                    "keyword_text": f"Budget increase from {up['campaign_name']}",
                    "match_type": "N/A",
                    "current_value": hp["budget"],
                    "recommended_value": new_hp_budget,
                    "recommendation_type": "BUDGET_REDISTRIBUTION",
                    "reason": f"Campaign is highly profitable (ACOS {hp['acos']:.1%}) and running out of budget ({hp['spend_ratio']:.0%} spent). Adding ${transfer_amount:.2f} transferred from {up['campaign_name']}.",
                    "source": "Budget Engine",
                    "metrics": {
                        "clicks": 0,
                        "spend": hp["spend"],
                        "sales": hp["sales"],
                        "orders": 0,
                        "acos": hp["acos"]
                    }
                })
                
                acos_str = f"{up['acos']:.1%}" if up['sales'] > 0 else "N/A"
                recommendations.append({
                    "entity_type": "Campaign",
                    "campaign_name": up["campaign_name"],
                    "ad_group_name": "N/A",
                    "keyword_text": f"Budget decrease to support {hp['campaign_name']}",
                    "match_type": "N/A",
                    "current_value": up["budget"],
                    "recommended_value": new_up_budget,
                    "recommendation_type": "BUDGET_REDISTRIBUTION",
                    "reason": f"Campaign is underperforming (ACOS {acos_str}) and has excess budget. Reducing budget by ${transfer_amount:.2f} to fund highly profitable campaigns.",
                    "source": "Budget Engine",
                    "metrics": {
                        "clicks": 0,
                        "spend": up["spend"],
                        "sales": up["sales"],
                        "orders": 0,
                        "acos": up["acos"]
                    }
                })
                
                # Update local tracker
                up["leftover"] -= transfer_amount
                up["budget"] = new_up_budget
                if up["leftover"] < 2.0:
                    under_performers.pop(0)
                    
    # Also alert if campaign is out of budget but no underperformer is available
    for hp in high_performers:
        # Check if already added in redistribution
        already_added = any(r["campaign_name"] == hp["campaign_name"] for r in recommendations)
        if not already_added:
            recommendations.append({
                "entity_type": "Campaign",
                "campaign_name": hp["campaign_name"],
                "ad_group_name": "N/A",
                "keyword_text": "Increase Daily Budget",
                "match_type": "N/A",
                "current_value": hp["budget"],
                "recommended_value": hp["budget"] * 1.2, # Suggest 20% increase
                "recommendation_type": "BUDGET_REDISTRIBUTION",
                "reason": f"Out of budget alert: Profitably spent {hp['spend_ratio']:.1%} of daily budget (${hp['budget']:.2f}) with ACOS {hp['acos']:.1%}.",
                "source": "Budget Alert",
                "metrics": {
                    "clicks": 0,
                    "spend": hp["spend"],
                    "sales": hp["sales"],
                    "orders": 0,
                    "acos": hp["acos"]
                }
            })
            
    return recommendations


def harvest_keywords(
    search_terms: List[Dict[str, Any]],
    target_acos: float
) -> List[Dict[str, Any]]:
    """
    Scans search term rows and flags terms that have sales and a profitable ACOS
    to be harvested as new targeted keywords.
    """
    new_keywords = []
    for term in search_terms:
        clicks = int(term.get("clicks", 0))
        spend = float(term.get("spend", 0.0))
        sales = float(term.get("sales", 0.0))
        orders = int(term.get("orders", 0))
        term_text = term.get("search_term") or term.get("customer_search_term")
        
        if not term_text:
            continue
            
        acos = (spend / sales) if sales > 0 else 0.0
        
        # If the term has sales and ACOS is profitable (<= Target ACOS)
        if orders >= 1 and sales > 0 and acos <= target_acos:
            # Set starting bid 10% above current CPC to ensure high visibility/win rate
            current_cpc = spend / clicks if clicks > 0 else 0.50
            recommended_bid = round(current_cpc * 1.10, 2)
            
            new_keywords.append({
                "entity_type": "SearchTerm",
                "campaign_name": term.get("campaign_name", "Unknown Campaign"),
                "ad_group_name": term.get("ad_group_name", "Unknown Ad Group"),
                "keyword_text": term_text,
                "match_type": "Exact", # Exact is best for scaling specific profitable queries
                "current_value": 0.0,
                "recommended_value": recommended_bid,
                "recommendation_type": "KEYWORD_HARVESTING",
                "reason": f"High converting query: Generated {orders} orders (${sales:.2f} sales) with profitable ACOS ({acos:.1%}). Promoted to Exact target to scale sales.",
                "source": term.get("source", "Report"),
                "metrics": {
                    "clicks": clicks,
                    "spend": spend,
                    "sales": sales,
                    "orders": orders,
                    "acos": acos
                }
            })
    return new_keywords

