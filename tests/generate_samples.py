import os
import pandas as pd

TEST_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_csv_report():
    csv_path = os.path.join(TEST_DIR, "sample_search_terms.csv")
    data = {
        "Campaign Name": [
            "Campaign SP - Desk Organizers", 
            "Campaign SP - Desk Organizers", 
            "Campaign SP - Desk Organizers", 
            "Campaign SP - Desk Organizers"
        ],
        "Ad Group Name": [
            "Bamboo Sets", 
            "Bamboo Sets", 
            "Metal Trays", 
            "Metal Trays"
        ],
        "Customer Search Term": [
            "cheap trashy plastic shelf", 
            "wooden cabinet with keys", 
            "mesh paper tray holder", 
            "free office giveaways"
        ],
        "Impressions": [1500, 2200, 800, 950],
        "Clicks": [12, 15, 8, 9],
        "Spend": [18.00, 22.10, 6.40, 7.20],
        "7 Day Total Sales": [0.00, 0.00, 45.00, 0.00],
        "7 Day Total Orders": [0, 0, 1, 0]
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    print(f"✓ Created mock search terms report: {csv_path}")

def generate_excel_bulk_sheet():
    xlsx_path = os.path.join(TEST_DIR, "sample_bulk_sheet.xlsx")
    
    # Sponsored Products Campaigns worksheet data
    sp_data = {
        "Product": ["Sponsored Products"] * 8,
        "Entity": ["Campaign", "Ad Group", "Keyword", "Keyword", "Campaign", "Ad Group", "Keyword", "Keyword"],
        "Operation": [""] * 8,
        "State": ["enabled"] * 8,
        "Campaign Name": [
            "Campaign SP - Desk Organizers", "Campaign SP - Desk Organizers", "Campaign SP - Desk Organizers", "Campaign SP - Desk Organizers",
            "Campaign SP - Ergonomic Chairs", "Campaign SP - Ergonomic Chairs", "Campaign SP - Ergonomic Chairs", "Campaign SP - Ergonomic Chairs"
        ],
        "Ad Group Name": [
            None, "Bamboo Sets", "Bamboo Sets", "Bamboo Sets",
            None, "Premium Highback", "Premium Highback", "Premium Highback"
        ],
        "Keyword Text": [
            None, None, "desk shelf organizer", "wood desk organizer",
            None, None, "ergonomic chair office", "gaming chair for desk"
        ],
        "Match Type": [
            None, None, "Exact", "Phrase",
            None, None, "Exact", "Broad"
        ],
        "Bid": [
            None, None, 1.20, 0.95,
            None, None, 2.50, 1.80
        ],
        "Campaign Daily Budget": [
            50.0, None, None, None,
            100.0, None, None, None
        ],
        "Clicks": [115, 115, 45, 12, 38, 38, 25, 18],
        "Spend": [47.50, 47.50, 40.50, 9.60, 35.00, 35.00, 62.50, 32.40],
        "Sales": [260.00, 260.00, 225.00, 32.00, 84.00, 84.00, 150.00, 0.00],
        "Orders": [12, 12, 10, 1, 2, 2, 3, 0]
    }
    df_sp = pd.DataFrame(sp_data)
    
    # Portfolio worksheet (empty placeholders for completeness)
    df_portfolios = pd.DataFrame(columns=["Portfolio ID", "Portfolio Name", "Budget", "State"])
    
    # Write multi-sheet Excel
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        df_sp.to_excel(writer, sheet_name="Sponsored Products Campaigns", index=False)
        df_portfolios.to_excel(writer, sheet_name="Portfolios", index=False)
        
    print(f"✓ Created mock Bulk Sheet workbook: {xlsx_path}")

if __name__ == "__main__":
    generate_csv_report()
    generate_excel_bulk_sheet()
