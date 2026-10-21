from pathlib import Path

main_file = Path("the_current_flutter/lib/main.dart")
source = main_file.read_text(encoding="utf-8")

# Give articles without a publisher-supplied image a relevant remote fallback.
source = source.replace(
    "article.imageUrl.isNotEmpty",
    "_imageUrl(article).isNotEmpty",
)
source = source.replace(
    "imageUrl: article.imageUrl",
    "imageUrl: _imageUrl(article)",
)

needle = "  Widget _imagePlaceholder({double width = double.infinity, double height = 130, bool dark = false}) => Container("
helper = """  String _imageUrl(NewsArticle article) {
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
if "_imageUrl(NewsArticle article)" not in source:
    if needle not in source:
        raise SystemExit("Could not locate image placeholder insertion point in main.dart")
    source = source.replace(needle, helper + needle, 1)

main_file.write_text(source, encoding="utf-8")
print("Applied image fallbacks to featured, list-card, and reader images.")
