from pathlib import Path

main_file = Path("the_current_flutter/lib/main.dart")
source = main_file.read_text(encoding="utf-8")

# Ensure every article image lookup goes through a resolver, not only one widget pattern.
source = source.replace("article.imageUrl", "_resolveImageUrl(article)")

helper = r"""String _resolveImageUrl(NewsArticle article, {bool fallbackOnly = false}) {
  final supplied = article.imageUrl.trim();
  if (!fallbackOnly && (supplied.startsWith('https://') || supplied.startsWith('http://'))) {
    return supplied;
  }

  final topic = '${article.category} ${article.title}'.toLowerCase();
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


# If a feed-provided URL fails, retry with the topic-specific fallback URL.
# Walk Image.network(...) expressions safely so nested widget arguments are preserved.
needle = "Image.network("
search_from = 0
while True:
    start = source.find(needle, search_from)
    if start < 0:
        break
    open_paren = start + len("Image.network") 
    depth, quote, escaped, end = 0, None, False, None
    for i in range(open_paren, len(source)):
        ch = source[i]
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\\\":
                escaped = True
            elif ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        raise SystemExit("Could not safely inspect Image.network call")
    call = source[start:end + 1]
    if "_resolveImageUrl(article" in call and "errorBuilder:" not in call:
        addition = ", errorBuilder: (context, error, stackTrace) => Image.network(_resolveImageUrl(article, fallbackOnly: true), fit: BoxFit.cover)"
        source = source[:end] + addition + source[end:]
        search_from = end + len(addition) + 1
    else:
        search_from = end + 1

main_file.write_text(source, encoding="utf-8")
print("Applied topic-aware fallback images to all article image references.")
