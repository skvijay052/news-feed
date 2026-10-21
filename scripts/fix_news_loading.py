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
  static const tamilFeedUrl = String.fromEnvironment(
    'TAMIL_FEED_URL',
    defaultValue: 'https://feeds.bbci.co.uk/tamil/rss.xml',
  );
  static const englishFeedUrl = String.fromEnvironment(
    'ENGLISH_FEED_URL',
    defaultValue: 'https://feeds.bbci.co.uk/news/world/rss.xml',
  );

  Future<List<NewsArticle>> fetchAll() async {
    final results = await Future.wait([
      _fetchOne(tamilFeedUrl, 'ta'),
      _fetchOne(englishFeedUrl, 'en'),
    ]);
    final articles = results.expand((items) => items).toList()
      ..sort((a, b) => (b.publishedAt ?? DateTime(2000))
          .compareTo(a.publishedAt ?? DateTime(2000)));
    return articles;
  }

  Future<List<NewsArticle>> _fetchOne(String endpoint, String language) async {
    try {
      final response = await http.get(Uri.parse(endpoint)).timeout(
        const Duration(seconds: 8),
      );
      if (response.statusCode != 200) return const [];
      final document = XmlDocument.parse(response.body);
      final articles = <NewsArticle>[];
      for (final item in document.findAllElements('item')) {
        String field(String name) => item.getElement(name)?.innerText.trim() ?? '';
        final title = field('title');
        final url = field('link');
        if (title.isEmpty || !url.startsWith('http')) continue;
        final rawDate = field('pubDate');
        final dateMatch = RegExp(
          r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})\s+(\d{2}):(\d{2}):(\d{2})',
        ).firstMatch(rawDate);
        DateTime? date;
        if (dateMatch != null) {
          const months = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,
            'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12};
          final month = months[dateMatch.group(2)!.toLowerCase()];
          if (month != null) {
            date = DateTime.tryParse(
              '${dateMatch.group(3)}-${month.toString().padLeft(2, '0')}-'
              '${dateMatch.group(1)!.padLeft(2, '0')}T${dateMatch.group(4)}:'
              '${dateMatch.group(5)}:${dateMatch.group(6)}Z',
            );
          }
        }
        var image = '';
        for (final element in item.descendants.whereType<XmlElement>()) {
          if (element.name.local == 'thumbnail' || element.name.local == 'content') {
            final candidate = element.getAttribute('url');
            if (candidate != null && candidate.startsWith('http')) {
              image = candidate;
              break;
            }
          }
        }
        final description = field('description')
            .replaceAll(RegExp(r'<[^>]*>'), ' ')
            .replaceAll(RegExp(r'\s+'), ' ')
            .trim();
        final category = field('category');
        articles.add(NewsArticle(
          id: url, title: title, url: url, language: language,
          summary: description, imageUrl: image,
          source: language == 'ta' ? 'BBC தமிழ்' : 'BBC News',
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
      url: 'https://tamilnews-feed.netlify.app/', language: 'ta',
      source: 'The Current Tamil', category: 'தமிழ்நாடு',
      publishedAt: DateTime.now(),
    ),
    NewsArticle(
      id: 'demo-en-1', title: 'Latest news from India and around the world',
      summary: 'Live headlines will appear here when a news feed is available.',
      url: 'https://newsfeed-current.netlify.app/', language: 'en',
      source: 'The Current', category: 'Top Stories',
      publishedAt: DateTime.now(),
    ),
    NewsArticle(
      id: 'demo-ta-2', title: 'தொழில்நுட்பம், வணிகம் மற்றும் விளையாட்டு',
      summary: 'தமிழ் செய்திகளைப் படிக்கவும், பிரிவுகளின் அடிப்படையில் தேடவும்.',
      url: 'https://tamilnews-feed.netlify.app/', language: 'ta',
      source: 'The Current Tamil', category: 'தொழில்நுட்பம்',
      publishedAt: DateTime.now().subtract(const Duration(minutes: 35)),
    ),
    NewsArticle(
      id: 'demo-en-2', title: 'Technology, business and world updates',
      summary: 'Browse the latest stories in one combined news app.',
      url: 'https://newsfeed-current.netlify.app/', language: 'en',
      source: 'The Current', category: 'Technology',
      publishedAt: DateTime.now().subtract(const Duration(minutes: 50)),
    ),
  ];
}
"""
repo_file.write_text(repo, encoding="utf-8")

spec = pubspec.read_text(encoding="utf-8")
if not re.search(r'(?m)^\s+xml\s*:', spec):
    match = re.search(r'(?m)^dependencies:\s*$', spec)
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
main, count = re.subn(
    r'if\s*\(loading\)\s*const\s+SliverFillRemaining\s*\(.*?\)\s*\n\s*else\s+if\s*\(stories\.isEmpty\)',
    'if (stories.isEmpty)',
    main, count=1, flags=re.S,
)
if count != 1:
    raise SystemExit("Could not remove the loading placeholder branch")
if "bool loading" in main or "if (loading)" in main or "CircularProgressIndicator" in main:
    raise SystemExit("A loading UI reference remains; refusing to produce a spinner build")
main_file.write_text(main, encoding="utf-8")
print("News feed patched: instant visible content, no loading UI, BBC Tamil/English RSS with timeout and offline fallback.")
