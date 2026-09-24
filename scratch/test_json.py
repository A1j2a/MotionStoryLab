import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.json_utils import extract_and_repair_json

test1 = '{\n  "title": "Farm Friends",\n  "lyrics": "Line 1\nLine 2\nLine 3",\n  "topics": [\n    "Item 1",\n    "Item 2",\n  ],\n}'
r1 = extract_and_repair_json(test1)
print("Test 1 Result:", bool(r1), r1.get("title") if r1 else "None")

test2 = '{"project": "Space Adventure", "scenes": [{"id": "1", "action": "rocket blasts off"'
r2 = extract_and_repair_json(test2)
print("Test 2 Result:", bool(r2), r2.get("project") if r2 else "None")
