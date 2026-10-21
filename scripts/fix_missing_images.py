from pathlib import Path

main_file = Path("the_current_flutter/lib/main.dart")
source = main_file.read_text(encoding="utf-8")

# Resolve a supplied image URL or use a relevant public fallback image.
source = source.replace("article.imageUrl.isNotEmpty", "_resolveImageUrl(article).isNotEmpty")
source = source.replace("imageUrl: article.imageUrl", "imageUrl: _resolveImageUrl(article)")

helper = """String _resolveImageUrl(NewsArticle article) {
  final supplied = article.imageUrl.trim();
  if (supplied.startsWith('https://') || supplied.startsWith('http://')) {
    return supplied;
  }

  final category = article.category.toLowerCase();
  final photo = category.contains('sport')
      ? 'photo-1461896836934-ffe607ba8211'
      : (category.contains('tech') || category.contains('தொழில்நுட்ப'))
          ? 'photo-1516321318423-f06f85e504b3'
          : (category.contains('business') || category.contains('வணிக'))
              ? 'photo-1486406146926-c627a92ad1ab'
              : article.language == 'ta'
                  ? 'photo-1495020689067-958852a7765e'
                  : 'photo-1504711434969-e33886168f5c';

  return 'https://images.unsplash.com/$photo?auto=format&fit=crop&w=1200&q=80';
}

"""
if "String _resolveImageUrl(NewsArticle article)" not in source:
    needle = "class TheCurrentApp extends StatelessWidget {"
    if needle not in source:
        raise SystemExit("Could not locate top-level insertion point in main.dart")
    source = source.replace(needle, helper + needle, 1)

main_file.write_text(source, encoding="utf-8")
print("Applied image fallbacks to featured, list-card, and reader images.")
