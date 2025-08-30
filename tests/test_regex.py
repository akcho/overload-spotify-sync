#!/usr/bin/env python3
import re

title = 'A trip-hop remix of Caroline Polachek "Pretty In Possible"'
title_lower = title.lower()

patterns = [
    r'^A\s+\w+[\w\-]*\s+remix\s+of\s+',  # Original pattern
    r'^A\s+[\w\-]+\s+remix\s+of\s+',     # Allow hyphens in the genre word
    r'^A\s+\w+\-\w+\s+remix\s+of\s+',   # Specifically for hyphenated genres
    r'^A\s+[\w\-]+\s+remix\s+of\s+',    # More permissive - any word chars and hyphens
    r'^A\s+[a-z\-]+\s+remix\s+of\s+',   # Just letters and hyphens
]

print(f"Title: '{title}'")
print(f"Title lower: '{title_lower}'")
print(f"First 20 chars: '{title_lower[:20]}'")
print()

# Let's test parts of the string manually
test_patterns = [
    r'^a\s+trip-hop\s+remix\s+of\s+',   # Exact match
    r'^a\s+[\w\-]+\s+remix\s+of\s+',   # Generic pattern
]

for i, pattern in enumerate(test_patterns, 1):
    match = re.search(pattern, title_lower)
    print(f"Test Pattern {i}: {pattern}")
    print(f"  Matches: {bool(match)}")
    if match:
        print(f"  Matched: '{match.group()}'")
    print()

# Also test the original patterns in case-insensitive mode
print("=== ORIGINAL PATTERNS ===")
for i, pattern in enumerate(patterns, 1):
    match = re.search(pattern, title_lower, re.IGNORECASE)
    print(f"Pattern {i}: {pattern}")
    print(f"  Matches: {bool(match)}")
    if match:
        print(f"  Matched: '{match.group()}'")
    print()