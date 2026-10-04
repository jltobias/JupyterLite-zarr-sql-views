"""Validate local HTML href/src targets in the assembled teaching site."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
ROOT=Path(__file__).resolve().parents[1]/'_site'
errors=[]
class Links(HTMLParser):
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key not in ('src','href') or not value:continue
            u=urlsplit(value)
            if u.scheme or u.netloc or not u.path:continue
            target=(ROOT/u.path.lstrip('/')) if u.path.startswith('/') else self.page.parent/unquote(u.path)
            if not target.exists():errors.append((str(self.page.relative_to(ROOT)),value))
for p in [ROOT/'index.html',ROOT/'lab/index.html',*list((ROOT/'book').rglob('*.html'))]:
    if '_static' in p.parts:continue # Theme Jinja templates are not navigable pages.
    parser=Links();parser.page=p;parser.feed(p.read_text(encoding='utf8'))
for p,value in errors:print(p,'->',value)
if errors:raise SystemExit(f'{len(errors)} broken local links')
print('Landing, lab, and book local links OK')
