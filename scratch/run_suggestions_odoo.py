import asyncio
import os
import sys

# Ensure app path is in import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.campaigns import generate_suggestions
from fastapi import Request
from starlette.datastructures import Headers, QueryParams

class MockRequest:
    def __init__(self, headers=None, query_params=None):
        self.headers = Headers(headers or {})
        self.query_params = QueryParams(query_params or {})

async def main():
    # Set environment to production (not testing mock)
    os.environ["TESTING"] = "false"
    os.environ["ENV"] = "production"
    
    mock_req = MockRequest()
    
    # Generate suggestions for Seller mode
    print("Generating suggestions for Seller Central (mode=seller) using Odoo data...")
    suggestions_seller = await generate_suggestions(
        request=mock_req,
        mode="seller",
        cached=False
    )
    print(f"Seller suggestions count: {len(suggestions_seller)}")
    for idx, s in enumerate(suggestions_seller):
        print(f"  {idx+1}: Type={s.get('recommendation_type')}, Campaign='{s.get('campaign_name')}', Entity='{s.get('keyword_text') or s.get('campaign_name')}', Recommended={s.get('recommended_value')}, Reason={s.get('reason')}")

    # Generate suggestions for Kindle mode
    print("\nGenerating suggestions for Kindle KDP (mode=kindle) using Odoo data...")
    suggestions_kindle = await generate_suggestions(
        request=mock_req,
        mode="kindle",
        cached=False
    )
    print(f"Kindle suggestions count: {len(suggestions_kindle)}")
    for idx, s in enumerate(suggestions_kindle):
        print(f"  {idx+1}: Type={s.get('recommendation_type')}, Campaign='{s.get('campaign_name')}', Entity='{s.get('keyword_text') or s.get('campaign_name')}', Recommended={s.get('recommended_value')}, Reason={s.get('reason')}")

if __name__ == "__main__":
    asyncio.run(main())
