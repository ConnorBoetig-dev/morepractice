#!/usr/bin/env python3
"""
Test rate limiting on API endpoints
"""
import requests
import time

API_BASE = "http://localhost:8000/api/v1"

def test_rate_limit(endpoint, limit):
    """Test rate limiting by making requests until we hit the limit"""
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint}")
    print(f"Expected limit: {limit} requests")
    print(f"{'='*60}")

    success_count = 0
    rate_limited_count = 0

    # Make more requests than the limit
    num_requests = limit + 10

    for i in range(1, num_requests + 1):
        try:
            response = requests.get(f"{API_BASE}{endpoint}")

            if response.status_code == 429:
                print(f"Request {i}: ❌ RATE LIMITED (429)")
                rate_limited_count += 1
            elif response.status_code == 200:
                print(f"Request {i}: ✅ OK (200)")
                success_count += 1
            else:
                print(f"Request {i}: Status {response.status_code}")

        except Exception as e:
            print(f"Request {i}: Error - {str(e)[:50]}")

    print(f"\n📊 Results:")
    print(f"  Success: {success_count}")
    print(f"  Rate Limited: {rate_limited_count}")
    print(f"  Expected to pass: ~{limit}")

    if rate_limited_count > 0:
        print(f"  ✅ Rate limiting is WORKING")
    else:
        print(f"  ⚠️  No rate limiting detected (may need more requests)")

if __name__ == "__main__":
    print("🔒 Rate Limiting Test Suite")
    print("Testing various API endpoints...\n")

    # Test standard endpoint (30/minute)
    test_rate_limit("/questions/exams", 30)

    # Test leaderboard endpoint (20/minute)
    test_rate_limit("/leaderboard/xp", 20)

    print(f"\n{'='*60}")
    print("✅ Rate Limiting Test Complete!")
    print(f"{'='*60}")
