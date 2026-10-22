from pathlib import Path

main_file = Path("the_current_flutter/lib/main.dart")
source = main_file.read_text(encoding="utf-8")

# Ensure every article image lookup goes through a resolver, not only one widget pattern.
source = source.replace("article.imageUrl", "_resolveImageUrl(article)")

helper = r"""String _resolveImageUrl(NewsArticle article) {
  final supplied = article.imageUrl.trim();
  if (supplied.startsWith('https://') || supplied.startsWith('http://')) {
    return supplied;
  }

  final topic = '\${article.category} \${article.title}'.toLowerCase();
  final photo = (topic.contains('sport') || topic.contains('cricket') ||
          topic.contains('football') || topic.contains('விளையாட்டு'))
      ? 'photo-1461896836934-ffe607ba8211'
      : (topic.contains('tech') || topic.contains('science') ||
              topic.contains('தொழில்நுட்பம்'))
          ? 'photo-1516321318423-f06f85e504b3'
          : (topic.contains('business') || topic.contains('market') ||
                  topic.contains('வணிகம்') || topic.contains('econom'))
              ? 'photo-1486406146926-c627a92ad1ab'
              : (topic.contains('entertainment') || topic.contains('cinema') ||
                      topic.contains('movie') || topic.contains('திரைப்படம்'))
                  ? 'photo-1489599849927-2ee91cede3ba'
                  : (topic.contains('health') || topic.contains('medical'))
                      ? 'photo-1505751172876-fa1923c5c528'
                      : (topic.contains('politic') || topic.contains('election'))
                          ? 'photo-1529107386315-e1a2ed48a620'
                          : (topic.contains('india') || topic.contains('தமிழ்நாடு'))
                              ? 'photo-1524492412937-b28074a5d7da'
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
print("Applied topic-aware fallback images to all article image references.")
