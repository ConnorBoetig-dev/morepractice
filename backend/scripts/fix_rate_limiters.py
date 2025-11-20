#!/usr/bin/env python3
"""
Helper script to fix rate limiter usage across all route files.

This script removes the manual limiter calls and adds the proper decorator imports.
Run this from the backend directory: python3 fix_rate_limiters.py
"""

import re
from pathlib import Path

# Files to fix
ROUTE_FILES = [
    "app/api/v1/question_routes.py",
    "app/api/v1/quiz_routes.py",
    "app/api/v1/achievement_routes.py",
    "app/api/v1/avatar_routes.py",
]

def fix_route_file(filepath):
    """Fix rate limiter usage in a route file"""
    print(f"\nProcessing {filepath}...")

    with open(filepath, 'r') as f:
        content = f.read()

    original_content = content

    # Step 1: Add import for limiter and RATE_LIMITS if not present
    if "from app.utils.rate_limit import" not in content:
        # Find the imports section and add our import
        import_pattern = r"(from sqlalchemy\.orm import Session\n)"
        replacement = r"\1\n# Import centralized rate limiter\nfrom app.utils.rate_limit import limiter, RATE_LIMITS\n"
        content = re.sub(import_pattern, replacement, content)
        print("  ✓ Added rate limiter import")

    # Step 2: Remove manual limiter calls (lines like: limiter = request.app.state.limiter)
    content = re.sub(r'\s*limiter = (?:request|http_request)\.app\.state\.limiter\n', '', content)
    content = re.sub(r'\s*await limiter\.limit\(["\'][^"\']+["\']\)\((?:request|http_request)\)\n', '', content)
    print("  ✓ Removed manual limiter calls")

    # Step 3: Remove Request parameter if it's no longer used
    # This is tricky - we'll check if Request is used elsewhere
    if 'request: Request' in content and 'Request' not in content.replace('request: Request', ''):
        # Remove Request from imports if not used
        content = re.sub(r', Request(?=\n|$)', '', content)
        content = re.sub(r'Request, ', '', content)
        print("  ✓ Removed unused Request import")

    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✅ Fixed {filepath}")
        return True
    else:
        print(f"  ⏭  No changes needed for {filepath}")
        return False

def main():
    """Fix all route files"""
    print("=" * 60)
    print("Fixing Rate Limiter Usage in Route Files")
    print("=" * 60)

    fixed_count = 0
    for filepath in ROUTE_FILES:
        if Path(filepath).exists():
            if fix_route_file(filepath):
                fixed_count += 1
        else:
            print(f"  ⚠  File not found: {filepath}")

    print("\n" + "=" * 60)
    print(f"Summary: Fixed {fixed_count} file(s)")
    print("=" * 60)
    print("\nNOTE: You still need to manually add @limiter.limit() decorators")
    print("to each route function. See auth_routes.py for examples.")
    print("\nExample:")
    print("  @router.get('/endpoint')")
    print("  @limiter.limit(RATE_LIMITS['standard'])  # Add this line")
    print("  async def my_endpoint(request: Request, ...):")
    print("=" * 60)

if __name__ == "__main__":
    main()
