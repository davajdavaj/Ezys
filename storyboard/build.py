"""Builds storyboard.html from shots.json and frames/, ready for PDF rendering."""
import json, base64, io, html
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
shots = json.load(open(ROOT / "shots.json"))

# Location report frames get the Ežys news ticker, as in the on-air format.
TICKER_FRAMES = {"3", "4a", "4b", "5", "10", "11", "12", "13a", "13b", "14"}
TICKER = ("Sunflower seed shellers are now peeling mandarins. ✓ After tasting mandarins, Popeye gave up spinach. "
          "✓ The snow angel has peeled off. ✓ After eating mandarins, the cow gave lemonade. ✓ Mandarins still rule.")


def img_data(name, width=1376):
    im = Image.open(ROOT / "frames" / f"{name}.png").convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def esc(s):
    return html.escape(s)


def line_with_tags(s):
    out = esc(s)
    for tag in ("[VFX]", "[CGI]"):
        out = out.replace(esc(tag), f'<span class="tag">{tag[1:-1]}</span>')
    return out


def logo_diamond(size="small"):
    return f'<div class="diamond {size}"><div class="d-inner"><span class="tick"></span><span>ežys</span></div></div>'


def frame_visual(s):
    sid = s["id"]
    if sid == "16":
        return f'''<div class="shot endcard">
          <div class="wordmark">e<span class="z">z<span class="tick big"><i></i></span></span>ys</div>
          <div class="nonsense">AND NO NONSENSE</div></div>'''
    fname = "f" + (sid.zfill(2) if sid.isdigit() else sid.zfill(3).lower())
    overlay = ""
    if sid in TICKER_FRAMES:
        overlay = f'''<div class="ticker"><div class="hashtag">#ezysgyvai</div>
          <div class="ticker-bar"><span>{esc(TICKER)}</span></div>{logo_diamond()}</div>'''
    if sid == "15":
        overlay = '''<div class="offer"><div>ORDER THE<br>EŽYS PLAN<br>AND WIN</div>
          <div class="offer-pink">EŽYS LEMONADE!</div></div>'''
    memory = '<div class="memory">MEMORY</div>' if s["scene"].startswith("MEMORY") else ""
    return f'<div class="shot"><img src="{img_data(fname)}">{overlay}{memory}</div>'


def audio_block(a):
    if not a:
        return '<div class="audio empty">No dialogue</div>'
    if ":" in a:
        who, line = a.split(":", 1)
        return f'<div class="audio"><b>{esc(who)}</b>{esc(line)}</div>'
    return f'<div class="audio">{esc(a)}</div>'


def row(s):
    return f'''<div class="row">
      {frame_visual(s)}
      <div class="text">
        <div class="num">{esc(s["id"])}</div>
        <div class="scene">{esc(s["scene"])}</div>
        <p class="l1">{line_with_tags(s["l1"])}</p>
        <p class="l2">{esc(s["l2"])}</p>
        {audio_block(s["audio"])}
      </div></div>'''


pages = []
cover_img = img_data("f04a", 1376)
pages.append(f'''<section class="page cover">
  <img class="cover-img" src="{cover_img}">
  <div class="cover-text">
    <div class="eyebrow">EŽYS · CHRISTMAS ’26 · TVC STORYBOARD</div>
    <h1>Pinocchio has<br>entered his teens</h1>
    <div class="meta">Director: Mitra<br>Agency: Truth · Production: Some Films<br>October 2026</div>
  </div>
</section>''')

pages.append('''<section class="page approach">
  <div class="header"><span>EŽYS · PINOCCHIO</span><span>HOW WE SHOOT IT</span></div>
  <h2>Two camera languages, one joke</h2>
  <div class="cols">
    <div class="col">
      <div class="k">News studio</div>
      <p>Shot like a real TV news show. Bright studio light, level frames, smooth and confident dolly moves. Rita and Benas never blink.</p>
      <div class="k">Pinocchio’s home</div>
      <p>Handheld, like a real news crew on location. The camera reacts, it never anticipates. The Ežys ticker runs under every report shot.</p>
      <div class="k">Memories</div>
      <p>Quick flashbacks under his voice. Same handheld eye, so they feel like footage of his life, not a different film.</p>
    </div>
    <div class="col">
      <div class="k">The story</div>
      <p>The mandarin is his first zit. He tries to pull it off, he tries to hide it, and in the end he lies about it. Every lie makes the nose longer, until it knocks over the Christmas tree and becomes a new one.</p>
      <div class="k">Lithuania, not America</div>
      <p>A Soviet era apartment: herringbone parquet, a dark wall unit, a cast iron radiator under lace curtains, straw ornaments on a real spruce. The school has two tone painted walls, paper snowflakes on the windows and a cloakroom with coat hooks. No lockers. Door sign in Lithuanian on set.</p>
      <div class="k">Colour on the board</div>
      <p>Everything in greyscale. Orange only for mandarins, teal only for Ežys, red only for the reporter’s Christmas tie.</p>
    </div>
  </div>
</section>''')

for i in range(0, len(shots), 2):
    pair = shots[i:i + 2]
    n = len(pages) - 1
    pages.append(f'''<section class="page board">
      <div class="header"><span>EŽYS · PINOCCHIO</span><span>STORYBOARD · {n}</span></div>
      {"".join(row(s) for s in pair)}
    </section>''')

css = (ROOT / "style.css").read_text()
html_doc = f'''<!doctype html><html><head><meta charset="utf-8"><title>Ezys Pinocchio Storyboard</title>
<style>{css}</style></head><body>{"".join(pages)}</body></html>'''
(ROOT / "storyboard.html").write_text(html_doc)
print("pages:", len(pages))
