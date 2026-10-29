"""Entry point: python3 -m backend.graph.parsers"""
from backend.graph.parsers import load_all_findings
from collections import Counter

fs = load_all_findings()
print("Total findings: {}".format(len(fs)))

print("\nBy type:")
for t, n in Counter(f.type for f in fs).most_common():
    print("  {}: {}".format(t, n))

print("\nBy severity:")
for s, n in Counter(f.severity for f in fs).most_common():
    print("  {}: {}".format(s, n))

print("\nBy source:")
for s, n in Counter(f.source for f in fs).most_common():
    print("  {}: {}".format(s, n))
