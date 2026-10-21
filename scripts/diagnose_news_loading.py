from pathlib import Path
import re

root = Path("the_current_flutter/lib")
main_file = root / "main.dart"
if not main_file.exists():
    raise SystemExit("Cannot diagnose: extracted lib/main.dart is missing")

print("=== NEWS FEED REPOSITORY IMPLEMENTATION ===")
for name in ("news_repository.dart", "news_article.dart"):
    file = root / name
    print(f"\\n--- {name} ---")
    if file.exists():
        print(file.read_text(encoding="utf-8"))
    else:
        print("FILE MISSING")
print("\\n=== MAIN APP LOADING FLOW ===")
source = main_file.read_text(encoding="utf-8")
lines = source.splitlines()
for start, end in ((0, 115), (125, 165)):
    print(f"\\n--- main.dart lines {start+1}-{min(end, len(lines))} ---")
    for i in range(start, min(end, len(lines))):
        print(f"{i+1}: {lines[i]}")
print("\\n=== END NEWS FEED DIAGNOSTICS ===")
