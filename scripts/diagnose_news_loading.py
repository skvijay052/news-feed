from pathlib import Path
import re

path = Path("the_current_flutter/lib/main.dart")
if not path.exists():
    raise SystemExit("Cannot diagnose: extracted lib/main.dart is missing")
source = path.read_text(encoding="utf-8")
print("=== NEWS FEED SOURCE DIAGNOSTICS ===")
print("main.dart characters:", len(source))
print("Dart imports:")
for line in source.splitlines():
    if line.lstrip().startswith("import "):
        print(line)
print("\nRelevant source lines (network, endpoints, parsing, loading/error states):")
lines = source.splitlines()
patterns = re.compile(r"https?://|Uri\.|http\.|dio\.|jsonDecode|fromJson|FutureBuilder|StreamBuilder|ConnectionState|CircularProgressIndicator|snapshot\.hasError|snapshot\.hasData|loading|Loading|fetch|NewsArticle|articles|error", re.I)
matches = [i for i, line in enumerate(lines) if patterns.search(line)]
shown = set()
for i in matches:
    for j in range(max(0, i-2), min(len(lines), i+3)):
        if j not in shown:
            print(f"{j+1}: {lines[j]}")
            shown.add(j)
    print("---")
print("=== END NEWS FEED SOURCE DIAGNOSTICS ===")
