"""Validate local HTML links and package only public prototype files."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import shutil

ROOT = Path(__file__).resolve().parents[1]
pages = sorted(ROOT.glob('CatSimba_*.html')) + [ROOT / 'index.html']
assert pages and (ROOT / 'CatSimba_Home.html').is_file(), 'Missing homepage'
names = {p.name for p in pages}


class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key not in ('href', 'src') or not value:
                continue
            url = urlsplit(value)
            if url.scheme or url.netloc or not url.path:
                continue
            target = unquote(url.path).removeprefix('./')
            if target not in names:
                raise ValueError(f'{self.source}: missing or unsupported local asset {value}')


for page in pages:
    parser = Links()
    parser.source = page.name
    parser.feed(page.read_text(encoding='utf-8'))

output = ROOT / 'dist'
output.mkdir(exist_ok=True)
# Fail if stale/unexpected files could accidentally be published.
allowed = names | {'index.html', 'robots.txt'}
assert all(p.is_file() and p.name in allowed for p in output.iterdir()), 'Unexpected files in dist; inspect before packaging'
for page in pages:
    shutil.copyfile(page, output / page.name)
(output / 'robots.txt').write_text('User-agent: *\nDisallow: /\n', encoding='utf-8')
print(f'Validated {len(pages)} pages; packaged into {output}')
