from pathlib import Path
import re

root = Path("the_current_flutter")
lib = root / "lib"
main_file = lib / "main.dart"
repo_file = lib / "news_repository.dart"
pubspec = root / "pubspec.yaml"
if not main_file.exists() or not repo_file.exists() or not pubspec.exists():
    raise SystemExit("Required Flutter source files are missing")

repo = r"""import 'package:http/http.dart' as http;
import 'package:xml/xml.dart';
import 'news_article.dart';

class NewsRepository {
  static const feeds = <({String url, String language, String source})>[
    (url: 'https://feeds.bbci.co.uk/tamil/rss.xml', language: 'ta', source: 'BBC தமிழ்'),
    (url: 'https://feeds.bbci.co.uk/news/india/rss.xml', language: 'en', source: 'BBC India'),
    (url: 'https://feeds.bbci.co.uk/news/world/rss.xml', language: 'en', source: 'BBC World'),
    (url: 'https://feeds.bbci.co.uk/news/technology/rss.xml', language: 'en', source: 'BBC Technology'),
    (url: 'https://feeds.bbci.co.uk/news/business/rss.xml', language: 'en', source: 'BBC Business'),
    (url: 'https://feeds.bbci.co.uk/sport/rss.xml', language: 'en', source: 'BBC Sport'),
    (url: 'https://news.google.com/rss/search?q=Tamil+Nadu&hl=ta&gl=IN&ceid=IN:ta', language: 'ta', source: 'Google News தமிழ்'),
    (url: 'https://news.google.com/rss/search?q=India+latest+news&hl=en-IN&gl=IN&ceid=IN:en', language: 'en', source: 'Google News India'),
    (url: 'https://news.google.com/rss/search?q=Chennai+news&hl=en-IN&gl=IN&ceid=IN:en', language: 'en', source: 'Google News Chennai'),
    (url: 'https://news.google.com/rss/search?q=technology+news&hl=en-IN&gl=IN&ceid=IN:en', language: 'en', source: 'Google News Technology'),
  ];

  Future<List<NewsArticle>> fetchAll() async {
    final results = await Future.wait(
      feeds.map((feed) => _fetchOne(feed.url, feed.language, feed.source)),
    );
    final byUrl = <String, NewsArticle>{};
    for (final article in results.expand((items) => items)) {
      byUrl.putIfAbsent(article.url, () => article);
    }
    final articles = byUrl.values.toList()
      ..sort((a, b) => (b.publishedAt ?? DateTime(2000))
          .compareTo(a.publishedAt ?? DateTime(2000)));
    return articles;
  }

  Future<List<NewsArticle>> _fetchOne(
    String endpoint, String language, String source,
  ) async {
    try {
      final response = await http.get(
        Uri.parse(endpoint),
        headers: const {'User-Agent': 'NewsFeed/1.0 (Android RSS Reader)'},
      ).timeout(const Duration(seconds: 12));
      if (response.statusCode != 200) return const [];
      final document = XmlDocument.parse(response.body);
      final articles = <NewsArticle>[];
      for (final item in document.findAllElements('item')) {
        String field(String name) =>
            item.children.whereType<XmlElement>()
                .where((element) => element.name.local == name)
                .map((element) => element.innerText.trim())
                .firstOrNull ?? '';
        final title = field('title');
        final url = field('link');
        if (title.isEmpty || !url.startsWith('http')) continue;
        final rawDate = field('pubDate');
        DateTime? date;
        try {
          date = HttpDate.parse(rawDate).toUtc();
        } catch (_) {
          date = DateTime.tryParse(rawDate)?.toUtc();
        }
        var image = '';
        for (final element in item.descendants.whereType<XmlElement>()) {
          if (element.name.local == 'thumbnail' ||
              element.name.local == 'content' ||
              element.name.local == 'enclosure') {
            final candidate = element.getAttribute('url') ??
                element.getAttribute('href');
            if (candidate != null && candidate.startsWith('http')) {
              image = candidate;
              break;
            }
          }
        }
        var description = field('description')
            .replaceAll(RegExp(r'<[^>]*>'), ' ')
            .replaceAll(RegExp(r'&nbsp;|&#160;'), ' ')
            .replaceAll(RegExp(r'\\s+'), ' ')
            .trim();
        description = description.replaceAll('&amp;', '&')
            .replaceAll('&quot;', '"').replaceAll('&#39;', "'");
        final category = field('category');
        articles.add(NewsArticle(
          id: url, title: title, url: url, language: language,
          summary: description, imageUrl: image, source: source,
          category: category.isEmpty ? 'Latest' : category,
          publishedAt: date,
        ));
      }
      return articles;
    } catch (_) {
      return const [];
    }
  }

  static final List<NewsArticle> sampleArticles = [
    NewsArticle(
      id: 'demo-ta-1', title: 'தமிழ்நாட்டின் முக்கிய செய்திகள்',
      summary: 'தமிழ் செய்தி ஊட்டம் கிடைக்கும்போது புதிய தலைப்புகள் இங்கே தோன்றும்.',
      url: 'https://news.google.com/', language: 'ta',
      source: 'News Feed', category: 'தமிழ்நாடு', publishedAt: DateTime.now(),
    ),
    NewsArticle(
      id: 'demo-en-1', title: 'Latest news from India and around the world',
      summary: 'Live headlines will appear here when a news feed is available.',
      url: 'https://news.google.com/', language: 'en',
      source: 'News Feed', category: 'Top Stories', publishedAt: DateTime.now(),
    ),
    NewsArticle(
      id: 'demo-ta-2', title: 'தொழில்நுட்பம், வணிகம் மற்றும் விளையாட்டு',
      summary: 'தமிழ் செய்திகளைப் படிக்கவும், பிரிவுகளின் அடிப்படையில் தேடவும்.',
      url: 'https://news.google.com/', language: 'ta',
      source: 'News Feed', category: 'தொழில்நுட்பம்',
      publishedAt: DateTime.now().subtract(const Duration(minutes: 35)),
    ),
    NewsArticle(
      id: 'demo-en-2', title: 'Technology, business and world updates',
      summary: 'Browse the latest stories in one combined news app.',
      url: 'https://news.google.com/', language: 'en',
      source: 'News Feed', category: 'Technology',
      publishedAt: DateTime.now().subtract(const Duration(minutes: 50)),
    ),
  ];
}
"""
repo_file.write_text(repo, encoding="utf-8")

spec = pubspec.read_text(encoding="utf-8")
if not re.search(r'(?m)^\s+xml\s*:', spec):
    match = re.search(r"(?m)^dependencies:\s*$", spec)
    if not match:
        raise SystemExit("Could not find dependencies section in pubspec.yaml")
    spec = spec[:match.end()] + "\n  xml: ^6.5.0" + spec[match.end():]
pubspec.write_text(spec, encoding="utf-8")

main = main_file.read_text(encoding="utf-8")
load_impl = r"""  Future<void> load() async {
    // Never wait for the network before showing the home feed.
    if (mounted && all.isEmpty) {
      setState(() => all = NewsRepository.sampleArticles);
    }
    try {
      final prefs = await SharedPreferences.getInstance();
      if (mounted) {
        setState(() {
          saved = prefs.getStringList('saved_article_ids')?.toSet() ?? {};
        });
      }
    } catch (_) {}
    try {
      final stories = await repository.fetchAll();
      if (mounted && stories.isNotEmpty) setState(() => all = stories);
    } catch (_) {
      // Keep the immediately visible content if the device is offline.
    }
  }
"""
pattern = r'  Future<void>\s+load\(\)\s+async\s*\{.*?\n  \}\n\n  Future<void>\s+toggleSaved'
main, count = re.subn(pattern, load_impl + "\n  Future<void> toggleSaved", main, count=1, flags=re.S)
if count != 1:
    raise SystemExit("Could not safely replace load()")
main = re.sub(r'(?m)^\s*bool loading = true;\s*\n', '', main)
# Refresh should reload immediately without referencing the removed loading flag.
main = main.replace('setState(() => loading = true); load();', 'load();')
main, count = re.subn(
    r'if\s*\(loading\)\s*const\s+SliverFillRemaining\s*\(.*?\)\s*\n\s*else\s+if\s*\(stories\.isEmpty\)',
    'if (stories.isEmpty)',
    main, count=1, flags=re.S,
)
if count != 1:
    raise SystemExit("Could not remove the loading placeholder branch")
if "bool loading" in main or "if (loading)" in main or "CircularProgressIndicator" in main:
    raise SystemExit("A loading UI reference remains; refusing to produce a spinner build")
# STORY DETAIL PAGE: open the publisher's full article inside the app.
if not re.search(r'(?m)^\s*webview_flutter\s*:', spec):
    match = re.search(r"(?m)^dependencies:\s*$", spec)
    if not match:
        raise SystemExit("Could not find dependencies section for webview_flutter")
    spec = spec[:match.end()] + "\n  webview_flutter: ^4.13.0" + spec[match.end():]
    pubspec.write_text(spec, encoding="utf-8")

if "package:webview_flutter/webview_flutter.dart" not in main:
    main = main.replace(
        "import 'package:url_launcher/url_launcher.dart';",
        "import 'package:url_launcher/url_launcher.dart';\nimport 'package:webview_flutter/webview_flutter.dart';",
        1,
    )

detail_widget = r'''
class NewsArticleDetailPage extends StatefulWidget {
  const NewsArticleDetailPage({super.key, required this.article});
  final NewsArticle article;

  @override
  State<NewsArticleDetailPage> createState() => _NewsArticleDetailPageState();
}

class _NewsArticleDetailPageState extends State<NewsArticleDetailPage> {
  late final WebViewController controller;

  @override
  void initState() {
    super.initState();
    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(NavigationDelegate())
      ..loadRequest(Uri.parse(widget.article.url));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.article.source, maxLines: 1, overflow: TextOverflow.ellipsis),
      ),
      body: WebViewWidget(controller: controller),
    );
  }
}

'''
if "class NewsArticleDetailPage extends StatefulWidget" not in main:
    needle_class = "class TheCurrentApp extends StatelessWidget {"
    if needle_class not in main:
        raise SystemExit("Could not find insertion point for article detail page")
    main = main.replace(needle_class, detail_widget + needle_class, 1)

# Make each story card (including the featured story) open the in-app full article page.
route = "Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => NewsArticleDetailPage(article: "
main = main.replace(
    "itemBuilder: (context, index) => _storyCard(stories[index]),",
    "itemBuilder: (context, index) => InkWell(\n"
    "                    onTap: () => Navigator.of(context).push(MaterialPageRoute<void>(\n"
    "                      builder: (_) => NewsArticleDetailPage(article: stories[index]),\n"
    "                    )),\n"
    "                    child: _storyCard(stories[index]),\n"
    "                  ),",
    1,
)
main = main.replace(
    "SliverToBoxAdapter(child: _featured(stories.first)),",
    "SliverToBoxAdapter(child: InkWell(\n"
    "                onTap: () => Navigator.of(context).push(MaterialPageRoute<void>(\n"
    "                  builder: (_) => NewsArticleDetailPage(article: stories.first),\n"
    "                )),\n"
    "                child: _featured(stories.first),\n"
    "              )),",
    1,
)

# Remove any Read More / Read full story button widget, preserving valid widget-list syntax.
for label_pattern in [r"read\s+more", r"read\s+full\s+story"]:
    while True:
        m = re.search(label_pattern, main, flags=re.I)
        if not m:
            break
        # Find the nearest supported button constructor before the label.
        starts = [(main.rfind(name, 0, m.start()), name) for name in
                  ("TextButton", "ElevatedButton", "OutlinedButton", "FilledButton")]
        start, _ = max(starts)
        if start < 0:
            # If only a label exists, hide it rather than leave the old wording.
            main = main[:m.start()] + "Story" + main[m.end():]
            continue
        # Locate the constructor's balanced parenthesis end, respecting quoted strings.
        open_paren = main.find("(", start)
        depth, quote, escaped, end = 0, None, False, None
        for i in range(open_paren, len(main)):
            ch = main[i]
            if quote:
                if escaped:
                    escaped = False
                elif ch == "\\":
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
                    end = i + 1
                    break
        if end is None:
            raise SystemExit("Could not safely remove Read More button")
        main = main[:start] + "const SizedBox.shrink()" + main[end:]

if "NewsArticleDetailPage(article: stories[index])" not in main:
    raise SystemExit("Could not attach article detail navigation to story cards")
main_file.write_text(main, encoding="utf-8")
print("News feed patched: instant visible content, no loading UI, in-app full-story reader, and no Read More button.")

