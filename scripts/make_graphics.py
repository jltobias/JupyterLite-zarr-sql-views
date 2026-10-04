"""Original vector teaching graphics; geography derives from Natural Earth (public domain)."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/assets'; OUT.mkdir(parents=True,exist_ok=True)
data=json.loads((ROOT/'public/data/countries.geojson').read_text(encoding='utf8'))
paths=[]
for f in data['features']:
    g=f['geometry']; polygons=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    for rings in polygons:
        ring=rings[0]
        # Regional silhouette, including nearby islands, with geographic points.
        if not any(-20<x<55 and -36<y<38 for x,y,*_ in ring):continue
        if not all(-28<x<65 and -40<y<43 for x,y,*_ in ring):continue
        points=' '.join(f'{230+(x+18)*3.15:.1f},{70+(38-y)*3.25:.1f}' for x,y,*_ in ring)
        paths.append(f'<polygon points="{points}"/>')
land=''.join(paths)
art=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 540" role="img" aria-labelledby="title desc"><title id="title">Earth as a space-time cube</title><desc id="desc">Conceptual layers of Africa above a grid, with time running upward. Natural Earth public-domain boundaries.</desc><defs><linearGradient id="plate" x2="1" y2="1"><stop stop-color="#8fd7b6" stop-opacity=".2"/><stop offset="1" stop-color="#4ea6bc" stop-opacity=".04"/></linearGradient><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#547c82" stroke-width=".5"/></pattern></defs><circle cx="348" cy="247" r="218" fill="none" stroke="#27474f" stroke-dasharray="2 7"/><path d="M86 362L345 503L590 357" fill="none" stroke="#6b9599" stroke-width="1"/><path d="M86 362V130" stroke="#a3d7bf" stroke-width="1"/><text x="58" y="120" fill="#b1e5ca" font-family="monospace" font-size="12">TIME ↑</text><g fill="url(#plate)" stroke="#477780"><path d="M95 322L338 186L585 322L342 459Z"/><path d="M95 266L338 130L585 266L342 403Z"/><path d="M95 210L338 74L585 210L342 347Z"/></g><path d="M95 210L338 74L585 210L342 347Z" fill="url(#grid)" opacity=".65"/><g transform="translate(-112 0)" fill="#a8dfba" stroke="#173f3e" stroke-width=".7">{land}</g><g fill="#e8c47c"><circle cx="285" cy="206" r="5"/><circle cx="323" cy="286" r="4"/><circle cx="307" cy="162" r="4"/></g><path d="M285 206V331M323 286V399M307 162V274" stroke="#e8c47c" stroke-dasharray="3 5"/><rect x="365" y="374" width="236" height="64" rx="4" fill="#132b31" stroke="#4c7374"/><text x="382" y="398" fill="#9bb7b9" font-family="monospace" font-size="10">A QUESTION BECOMES A VIEW</text><text x="382" y="420" fill="#e8c47c" font-family="monospace" font-size="13">WHERE value &gt; threshold</text><text x="112" y="481" fill="#8caaa9" font-family="monospace" font-size="10">CONCEPTUAL GRAPHIC · NOT OBSERVATIONS</text></svg>'''
(OUT/'earth-cube.svg').write_text(art,encoding='utf8')
banner=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="620" viewBox="0 0 1440 620"><rect width="1440" height="620" fill="#0b191f"/><text x="85" y="105" fill="#b1e5ca" font-family="Arial,sans-serif" font-size="15" letter-spacing="4">EARTH / BROWSER</text><text x="85" y="242" fill="#e7efea" font-family="Arial,sans-serif" font-size="68">A changing Earth.</text><text x="85" y="325" fill="#b1e5ca" font-family="Arial,sans-serif" font-size="68">A new perspective.</text><text x="85" y="388" fill="#9eb3b6" font-family="Arial,sans-serif" font-size="23">Zarr + SQL + JupyterLite · An open teaching atlas</text><path d="M85 440H650" stroke="#2c454b"/><text x="85" y="484" fill="#e8c47c" font-family="Arial,sans-serif" font-size="17">12 LESSONS / 6 CUBES / ONE BROWSER</text><text x="85" y="552" fill="#9eb3b6" font-family="Arial,sans-serif" font-size="13">Inspired by dzole0311/zarr-sql-views · Digital Earth Africa · C3S Atlas</text><svg x="720" y="38" width="650" height="540" viewBox="0 0 650 540">{art.split('</desc>',1)[1].rsplit('</svg>',1)[0]}</svg></svg>'''
(OUT/'splash.svg').write_text(banner,encoding='utf8')
(OUT/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#10252c"/><path d="M32 9L55 22V43L32 56L9 43V22Z M9 22L32 35L55 22 M32 35V56" fill="none" stroke="#b1e5ca" stroke-width="3"/></svg>')
steps=[('01 / DISCOVER','STAC describes assets'),('02 / READ','Zarr chunks → arrays'),('03 / ASK','SQL selects local cells'),('04 / SEE','Maps + cubes + series')]
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 210"><rect width="1120" height="210" fill="#10252c"/>'
for i,(title,desc) in enumerate(steps):
    x=25+i*278
    svg+=f'<rect x="{x}" y="35" width="235" height="130" rx="8" fill="#19363e" stroke="#507777"/><text x="{x+18}" y="80" fill="#b1e5ca" font-family="Arial" font-size="17">{title}</text><text x="{x+18}" y="119" fill="#e7efea" font-family="Arial" font-size="15">{desc}</text>'
    if i<3:svg+=f'<text x="{x+247}" y="105" fill="#e8c47c" font-size="24">→</text>'
svg+='</svg>'
(OUT/'pipeline.svg').write_text(svg.encode('ascii','xmlcharrefreplace').decode('ascii'),encoding='ascii')
print('Wrote four original SVGs')
