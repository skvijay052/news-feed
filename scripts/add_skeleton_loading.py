from pathlib import Path
import re

main_file = Path("the_current_flutter/lib/main.dart")
if not main_file.exists():
    raise SystemExit("Flutter source not found: " + str(main_file))
source = main_file.read_text(encoding="utf-8")

if "class NewsFeedSkeletonList" not in source:
    widget = r'''
class NewsFeedSkeletonList extends StatelessWidget {
  const NewsFeedSkeletonList({super.key, this.itemCount = 5});

  final int itemCount;

  @override
  Widget build(BuildContext context) {
    final base = Theme.of(context).brightness == Brightness.dark
        ? const Color(0xFF292929)
        : const Color(0xFFE8E8E8);
    final highlight = Theme.of(context).brightness == Brightness.dark
        ? const Color(0xFF383838)
        : const Color(0xFFF5F5F5);

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      itemCount: itemCount,
      itemBuilder: (context, index) => Padding(
        padding: const EdgeInsets.only(bottom: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              height: 190,
              width: double.infinity,
              decoration: BoxDecoration(
                color: base,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Align(
                alignment: Alignment.topLeft,
                child: Container(
                  margin: const EdgeInsets.all(12),
                  width: 76,
                  height: 22,
                  decoration: BoxDecoration(
                    color: highlight,
                    borderRadius: BorderRadius.circular(6),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),
            Container(
              height: 16,
              width: double.infinity,
              decoration: BoxDecoration(
                color: base,
                borderRadius: BorderRadius.circular(5),
              ),
            ),
            const SizedBox(height: 8),
            Container(
              height: 16,
              width: MediaQuery.of(context).size.width * 0.62,
              decoration: BoxDecoration(
                color: base,
                borderRadius: BorderRadius.circular(5),
              ),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Container(
                  height: 10,
                  width: 82,
                  decoration: BoxDecoration(
                    color: highlight,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const SizedBox(width: 12),
                Container(
                  height: 10,
                  width: 56,
                  decoration: BoxDecoration(
                    color: highlight,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

'''
    # Insert before the first app/root widget, or prepend after imports.
    m = re.search(r'class\s+\w+\s+extends\s+(?:StatelessWidget|StatefulWidget)\s*\{', source)
    if not m:
        raise SystemExit("Could not find a Flutter widget insertion point in main.dart")
    source = source[:m.start()] + widget + source[m.start():]

# Replace common API waiting branches with skeleton cards. This deliberately targets
# explicit FutureBuilder/StreamBuilder waiting states, not general loading spinners.
patterns = [
    (r'if\s*\(\s*snapshot\.connectionState\s*==\s*ConnectionState\.waiting\s*\)\s*\{\s*return\s+const?\s*Center\s*\(\s*child\s*:\s*CircularProgressIndicator\s*\(\s*\)\s*,?\s*\)\s*;?\s*\}',
     'if (snapshot.connectionState == ConnectionState.waiting) { return const NewsFeedSkeletonList(); }'),
    (r'if\s*\(\s*snapshot\.connectionState\s*==\s*ConnectionState\.waiting\s*\)\s*return\s+const?\s*Center\s*\(\s*child\s*:\s*CircularProgressIndicator\s*\(\s*\)\s*,?\s*\)\s*;',
     'if (snapshot.connectionState == ConnectionState.waiting) return const NewsFeedSkeletonList();'),
]
for pattern, replacement in patterns:
    source = re.sub(pattern, replacement, source)

# Also replace the common direct FutureBuilder loading expression.
source = re.sub(
    r'CircularProgressIndicator\s*\(\s*\)',
    'const NewsFeedSkeletonList()',
    source
)

main_file.write_text(source, encoding="utf-8")
print("Added NewsFeedSkeletonList and switched common loading placeholders to skeleton cards.")
