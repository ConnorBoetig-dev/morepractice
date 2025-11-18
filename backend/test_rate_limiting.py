#!/usr/bin/env python3
"""
Simple script to test rate limiting on API endpoints
"""

import requests
import time

API_BASE = "http://localhost:8000/api/v1"

def test_endpoint(name, url, method="GET", data=None):
    """Test an endpoint with multiple requests"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    for i in range(1, 4):
        try:
            if method == "GET":
                response = requests.get(url)
            else:
                response = requests.post(url, json=data)

            print(f"Request {i}: Status {response.status_code}", end="")
            if response.status_code == 429:
                print(" - RATE LIMITED ✓")
            elif response.status_code < 300:
                print(" - OK")
            else:
                print(f" - Error: {response.text[:50]}")
        except Exception as e:
            print(f"Request {i}: Error - {str(e)[:50]}")

        time.sleep(0.1)  # Small delay between requests

if __name__ == "__main__":
    print("Rate Limiting Test Suite")
    print("Testing various API endpoints...\n")

    # Test public endpoints
    test_endpoint(
        "Questions - Get Exams",
        f"{API_BASE}/questions/exams"
    )

    test_endpoint(
        "Leaderboard - XP",
        f"{API_BASE}/leaderboard/xp"
    )

    test_endpoint(
        "Auth - Login",
        f"{API_BASE}/auth/login",
        method="POST",
        data={"email": "test@example.com", "password": "test"}
    )

    print(f"\n{'='*60}")
    print("Rate Limiting Test Complete!")
    print(f"{'='*60}")
    print("\nNote: To properly test rate limiting, run many requests rapidly")
    print("The decorator limits are: 30/minute for standard, 10/minute for quiz submit, etc.")
