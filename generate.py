#!/usr/bin/env python3
"""Builds every page of the site from one template.
Change SITE_URL to your real domain, then run:  python3 generate.py
"""
import json, os, html

SITE_URL = "https://goldrateinpakistan.netlify.app"
BRAND = "TolaRate"
OUT = os.path.dirname(os.path.abspath(__file__))

CITIES = [
    ("lahore", "Lahore", "لاہور"), ("karachi", "Karachi", "کراچی"), ("islamabad", "Islamabad", "اسلام آباد"),
    ("rawalpindi", "Rawalpindi", "راولپنڈی"), ("faisalabad", "Faisalabad", "فیصل آباد"), ("multan", "Multan", "ملتان"),
    ("peshawar", "Peshawar", "پشاور"), ("quetta", "Quetta", "کوئٹہ"), ("sialkot", "Sialkot", "سیالکوٹ"),
    ("hyderabad", "Hyderabad", "حیدرآباد"), ("gujranwala", "Gujranwala", "گوجرانوالہ"),
]
KARAT_INFO = {
    24: "24K is pure gold (99.9%). It’s mostly bought as bars and coins for investment rather than for jewellery, because pure gold is soft.",
    22: "22K gold is 91.7% gold. Some jewellers, especially in Lahore, quote jewellery prices on the 22K rate.",
    21: "21K gold is 87.5% gold and is used for almost all jewellery made in Pakistan, so it’s the rate most families need.",
    18: "18K gold is 75% gold. It’s harder and cheaper, so it’s common in modern and stone-set jewellery.",
}

OFFICIAL = json.load(open(os.path.join(OUT, "rates.json")))

def e(s): return html.escape(s, quote=True)

# ---- today's official numbers, written straight into the HTML so Google can read them
from datetime import date as _date
G_TOLA = 11.6638
OFF_DATE = _date.fromisoformat(OFFICIAL["date"])
DATE_LONG = f"{OFF_DATE.day} {OFF_DATE.strftime('%B %Y')}"
DATE_SHORT = f"{OFF_DATE.day} {OFF_DATE.strftime('%b %Y')}"
def rs(n): return "Rs " + f"{round(n):,}"
def tola(k, t24=None): return (t24 or OFFICIAL["tola24"]) * k / 24
def g10(k): return (OFFICIAL.get("gram10_24") or OFFICIAL["tola24"] / G_TOLA * 10) * k / 24
PURITY = {24: "99.9% pure", 22: "91.7% gold", 21: "87.5% gold", 18: "75% gold"}

def answer_text(place, k):
    others = [x for x in (24, 22, 21, 18) if x != k]
    return (f"Today’s official {k}K gold rate in {place} is {rs(tola(k))} per tola and {rs(g10(k))} per 10 gram, "
            f"as issued by the All Pakistan Sarafa Gems and Jewellers Association on {DATE_LONG}. "
            + ", ".join(f"{x}K is {rs(tola(x))}" for x in others) + " per tola.")

def static_cards(t24, featured):
    out = []
    for k in (24, 22, 21, 18):
        pg = t24 * k / 24 / G_TOLA
        out.append(f'<article class="rate{" featured" if k == featured else ""}" data-k="{k}"><div class="k"><b>{k}K</b><small>{PURITY[k]}</small></div>'
                   f'<div class="tola">{rs(pg * G_TOLA)} <small>/ tola</small></div>'
                   f'<dl><dt>10 gram</dt><dd>{rs(pg * 10)}</dd><dt>1 gram</dt><dd>{rs(pg)}</dd></dl></article>')
    return "".join(out)

# ---------------------------------------------------------------- shared pieces
def head(title, desc, path, faqs, extra_kw=""):
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="keywords" content="{e(extra_kw)}">
<link rel="canonical" href="{SITE_URL}{path}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}{path}">
<meta name="theme-color" content="#0E5A43" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0F1613" media="(prefers-color-scheme: dark)">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🪙</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,700;12..96,800&family=Noto+Nastaliq+Urdu:wght@500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/base.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>"""

def topbar(active, mini_label):
    items = [("/", "Gold", "gold"), ("/silver-rate/", "Silver", "silver"), ("/dollar-rate/", "Dollar", "dollar"),
             ("/#calculator", "Calculator", "calc"), ("/#faq", "FAQ", "faq")]
    nav = "\n      ".join(f'<a href="{h}"{" aria-current=\"page\"" if k == active else ""}>{t}</a>' for h, t, k in items)
    return f"""<header class="topbar">
  <div class="wrap">
    <a class="brand" href="/" aria-label="{BRAND} home"><span class="coin" aria-hidden="true"></span><span>Tola<em>Rate</em></span></a>
    <nav class="topnav" aria-label="Main">
      {nav}
    </nav>
    <div class="mini-live num" aria-hidden="true"><small>{mini_label}</small><b id="miniPrice">—</b></div>
  </div>
</header>"""

def crumbs(trail):
    parts = ['<a href="/">Home</a>'] + [f'<a href="{h}">{t}</a>' if h else e(t) for t, h in trail]
    return '<p class="crumbs">' + " › ".join(parts) + "</p>"

def live_card(label, unit_note="10 gram", vs_label="Vs. Sarafa rate"):
    return f"""<div class="live-card" id="live" aria-live="polite">
        <span class="pill"><span class="dot" id="dot"></span><span id="status">Connecting to live price…</span></span>
        <p class="live-label">{label}</p>
        <p class="live-price num" id="livePrice">—</p>
        <div class="live-sub num">
          <span>{unit_note} <b id="live10g">—</b></span>
          <span>{vs_label} <span class="chg" id="liveVsOff">—</span></span>
        </div>
        <div class="live-foot">
          <span id="liveTime">Updates every 10 seconds</span>
          <button class="btn-ghost" id="refresh" type="button">Refresh now</button>
        </div>
      </div>"""

def official_card(k):
    return f"""<aside class="official" aria-labelledby="offTitle">
        <div class="official-top">
          <h2 id="offTitle">Official Sarafa rate</h2>
          <span class="tag" id="offDate">{DATE_SHORT}</span>
        </div>
        <p class="off-price num" id="offPrice">{rs(tola(k))}</p>
        <div class="off-meta num">
          <span>{k}K per tola</span>
          <span>10 gram <b id="off10g">{rs(g10(k))}</b></span>
          <span class="chg" id="offChg"></span>
        </div>
        <svg class="spark" id="spark" viewBox="0 0 300 64" preserveAspectRatio="none" role="img" aria-label="Official rate over recent days"></svg>
        <div class="spark-labels num"><span id="sparkFrom"></span><span id="sparkTo"></span></div>
        <div class="sources">Issued by the All Pakistan Sarafa Gems and Jewellers Association. Reported by <span id="sourceLinks">—</span>.</div>
      </aside>"""

def market_section(metal, title, sub):
    return f"""<section id="market">
    <div class="sec-head"><div>
      <h2 class="sec">{title}</h2>
      <p class="sub">{sub}</p>
    </div></div>
    <div class="market" id="marketBox" data-metal="{metal}"><p class="empty">Loading Sarafa market rates…</p></div>
  </section>"""

def rates_section(title, featured=21):
    return f"""<section id="rates">
    <div class="sec-head">
      <div>
        <h2 class="sec">{title}</h2>
        <p class="sub">Per tola, 10 gram and gram for the karats sold in Pakistan.</p>
      </div>
      <div class="seg" role="group" aria-label="Rate basis">
        <button type="button" data-basis="live" aria-pressed="true">Live</button>
        <button type="button" data-basis="official" aria-pressed="false">Sarafa</button>
      </div>
    </div>
    <div class="rate-grid num" id="rateGrid">{static_cards(OFFICIAL["tola24"], featured)}</div>
    <p class="basis-note" id="basisNote"></p>
  </section>"""

def intl_section(kind):
    if kind == "gold":
        stats = """<div class="stat"><small>Gold spot, per ounce</small><b id="spotUsd">—</b><span class="chg" id="spotChg"></span></div>
        <div class="stat"><small>1 US dollar</small><b id="usdPkr">—</b><span class="chg" style="color:var(--muted);font-weight:400">Interbank rate</span></div>
        <div class="stat"><small>Spot in rupees, per tola</small><b id="spotTola">—</b></div>
        <div class="stat"><small>Spot in dollars, per tola</small><b id="spotTolaUsd">—</b></div>"""
        sym, title, sub = "OANDA:XAUUSD", "International gold rate", "Gold in US dollars per ounce (XAU/USD). The chart streams prices as they trade."
    elif kind == "silver":
        stats = """<div class="stat"><small>Silver spot, per ounce</small><b id="spotUsd">—</b><span class="chg" id="spotChg"></span></div>"""
        sym, title, sub = "OANDA:XAGUSD", "International silver rate", "Silver in US dollars per ounce (XAG/USD), streaming as it trades."
    else:
        stats = ""
        sym, title, sub = "FX_IDC:USDPKR", "Dollar to rupee chart", "US dollar against the Pakistani rupee."
    side = f'<div class="intl-side num">{stats}<div class="stat wide quote-box" data-tv-quote="{sym}"></div></div>' if stats else ""
    grid_style = "" if stats else ' style="grid-template-columns:1fr"'
    return f"""<section id="international">
    <div class="sec-head"><div>
      <h2 class="sec">{title}</h2>
      <p class="sub">{sub}</p>
    </div></div>
    <div class="intl-grid"{grid_style}>
      {side}
      <div>
        <div class="chart-box" data-tv-chart="{sym}" data-tv-interval="{'60' if kind == 'dollar' else '1'}"><div class="chart-fallback">Loading live chart…</div></div>
        <p class="credit">Live chart by <a href="https://www.tradingview.com/" target="_blank" rel="noopener">TradingView</a>.</p>
      </div>
    </div>
  </section>"""

def calc_section():
    return """<section id="calculator">
    <div class="sec-head">
      <div>
        <h2 class="sec">Calculators</h2>
        <p class="sub">Work out jewellery prices and zakat using the live or the official Sarafa rate.</p>
      </div>
      <div class="seg" role="group" aria-label="Calculator rate basis">
        <button type="button" data-basis="live" aria-pressed="true">Live</button>
        <button type="button" data-basis="official" aria-pressed="false">Sarafa</button>
      </div>
    </div>
    <div class="calc-grid">
      <div class="panel">
        <div class="panel-head"><h3>Jewellery price</h3><p class="urdu">زیور کی قیمت</p></div>
        <label for="w">Weight</label>
        <div class="row">
          <input id="w" type="number" inputmode="decimal" min="0" step="any" value="1">
          <select id="wu" aria-label="Weight unit"><option value="tola">Tola</option><option value="gram">Gram</option><option value="masha">Masha</option><option value="ratti">Ratti</option></select>
        </div>
        <label id="karatLbl">Karat</label>
        <div class="chips" id="karatChips" role="group" aria-labelledby="karatLbl">
          <button type="button" data-k="24">24K</button><button type="button" data-k="22">22K</button><button type="button" data-k="21">21K</button><button type="button" data-k="18">18K</button>
        </div>
        <label for="mk">Making charges (%)</label>
        <input id="mk" type="number" inputmode="decimal" min="0" step="any" value="8">
        <div class="result num">
          <div class="line"><span>Gold value</span><b id="cGold">—</b></div>
          <div class="line"><span>Making charges</span><b id="cMake">—</b></div>
          <div class="total"><span>Estimated price</span><strong id="cTotal">—</strong></div>
          <p class="note">When you sell, jewellers usually deduct for wastage (kaat). Ask for their exact rate.</p>
        </div>
      </div>
      <div class="panel" id="zakat">
        <div class="panel-head"><h3>Zakat on gold</h3><p class="urdu">سونے پر زکوٰۃ</p></div>
        <label for="zw">Gold you own</label>
        <div class="row">
          <input id="zw" type="number" inputmode="decimal" min="0" step="any" value="10">
          <select id="zu" aria-label="Zakat weight unit"><option value="tola">Tola</option><option value="gram">Gram</option></select>
        </div>
        <label for="zk">Karat</label>
        <select id="zk"><option value="24">24K</option><option value="22">22K</option><option value="21">21K</option><option value="18">18K</option></select>
        <div class="result num">
          <div class="line"><span>Value of your gold</span><b id="zVal">—</b></div>
          <div class="line"><span>Nisab</span><b>7.5 tola of gold</b></div>
          <div class="total"><span>Zakat due (2.5%)</span><strong id="zDue">—</strong></div>
          <p class="verdict" id="zVerdict"></p>
          <p class="note">This covers gold only. If you also own cash, silver or other assets, scholars differ on how to combine them, so check with a scholar you trust.</p>
        </div>
      </div>
    </div>
  </section>"""

UNITS = """<section>
    <div class="sec-head"><div>
      <h2 class="sec">Weight units used by jewellers</h2>
      <p class="sub">Jewellers quote in tola, masha and ratti. Here is how they convert.</p>
    </div></div>
    <div class="units">
      <div class="unit"><b>1 tola</b><span>11.6638 gram</span></div>
      <div class="unit"><b>1 tola</b><span>12 masha</span></div>
      <div class="unit"><b>1 masha</b><span>8 ratti, 0.972 gram</span></div>
      <div class="unit"><b>1 ratti</b><span>0.1215 gram</span></div>
    </div>
  </section>"""

def faq_section(faqs):
    items = "\n      ".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faqs)
    return f"""<section id="faq">
    <div class="sec-head"><div><h2 class="sec">Common questions</h2></div></div>
    <div class="faq">
      {items}
    </div>
  </section>"""

def links_section(current):
    def li(href, text):
        cur = ' aria-current="page"' if href == current else ""
        return f'<li><a href="{href}"{cur}>{text}</a></li>'
    cities = "".join(li(f"/gold-rate-{s}/", n) for s, n, _ in CITIES)
    karats = "".join(li(f"/{k}k-gold-rate/", f"{k}K gold") for k in (24, 22, 21, 18))
    more = li("/", "Gold rate today") + li("/gold-rate-history/", "Gold rate history") + li("/silver-rate/", "Silver rate") + li("/dollar-rate/", "Dollar rate")
    return f"""<section id="more">
    <div class="sec-head"><div><h2 class="sec">More rates</h2></div></div>
    <div class="links">
      <div><h3>Gold rate by city</h3><ul>{cities}</ul></div>
      <div><h3>Gold rate by karat</h3><ul>{karats}</ul></div>
      <div><h3>Other rates</h3><ul>{more}</ul></div>
    </div>
  </section>"""

def refs_section(kind):
    items = []
    if kind in ("gold",):
        items.append(("Official daily rate", "All Pakistan Sarafa Gems and Jewellers Association, as reported by "
                      '<a href="https://arynews.tv/gold-rates-today-in-pakistan" target="_blank" rel="noopener">ARY News</a>, '
                      '<a href="https://en.dailypakistan.com.pk/" target="_blank" rel="noopener">Daily Pakistan</a> and '
                      '<a href="https://pakobserver.net/" target="_blank" rel="noopener">Pakistan Observer</a>.'))
    if kind in ("gold", "silver"):
        items.append(("Sarafa market rates, Rawalpindi", 'Checked automatically from '
                      f'<a href="https://goldstarjewellers.pk/{"today-gold-rate-in-pakistan" if kind == "gold" else "silver-rate-today-in-pakistan"}/" target="_blank" rel="noopener">Gold Star Jewellers</a>, Sarafa Bazar, Rawalpindi.'))
        items.append(("Compare with", '<a href="https://sarmaaya.pk/commodities/gold" target="_blank" rel="noopener">Sarmaaya</a> for live rates and history.'))
        items.append(("International prices", '<a href="https://gold-api.com/" target="_blank" rel="noopener">gold-api.com</a>, updated every few seconds.'))
    items.append(("Exchange rates", '<a href="https://www.exchangerate-api.com/" target="_blank" rel="noopener">ExchangeRate-API</a> (interbank rates, updated daily).'))
    items.append(("Charts", '<a href="https://www.tradingview.com/" target="_blank" rel="noopener">TradingView</a>.'))
    lis = "\n        ".join(f"<li><b>{t}</b><span>{d}</span></li>" for t, d in items)
    return f"""<section id="sources">
    <div class="sec-head"><div>
      <h2 class="sec">Sources</h2>
      <p class="sub">Where every number on this page comes from.</p>
    </div></div>
    <div class="refs"><ul>
        {lis}
    </ul></div>
  </section>"""

FOOTER = f"""<footer>
    <p>Live rates are estimates for information only and are not an offer to buy or sell. Always confirm the final price with your jeweller or bank.</p>
    <p>© <span id="yr"></span> {BRAND}</p>
  </footer>"""

def bottomnav(active):
    def a(href, label, key, icon, sec=""):
        cls = ' class="active"' if key == active else ""
        ds = f' data-sec="{sec}"' if sec else ""
        return f'<a href="{href}"{ds}{cls}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{icon}</svg>{label}</a>'
    coin = '<circle cx="12" cy="12" r="9"/><path d="M8 12h8M12 8v8"/>'
    silver = '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/>'
    dollar = '<path d="M12 3v18M16.5 7.5c0-1.7-2-3-4.5-3s-4.5 1.3-4.5 3.3c0 4.4 9 2.4 9 6.9 0 1.9-2 3.3-4.5 3.3s-4.5-1.3-4.5-3"/>'
    chart = '<path d="M3 17l5-5 4 4 8-9"/><path d="M15 7h5v5"/>'
    return ('<nav class="bottomnav" aria-label="Quick navigation">' +
            a("/", "Gold", "gold", coin) + a("/silver-rate/", "Silver", "silver", silver) +
            a("/dollar-rate/", "Dollar", "dollar", dollar) + a("#international", "Chart", "chart", chart, "international") +
            "</nav>")

def page(path, html_text):
    full = os.path.join(OUT, path.strip("/"), "index.html") if path != "/" else os.path.join(OUT, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(html_text)

FALLBACK_JS = "<script>window.OFFICIAL_FALLBACK = " + json.dumps(OFFICIAL) + ";</script>"

# ---------------------------------------------------------------- gold pages
BASE_FAQ = [
    ("Who sets the gold rate in Pakistan?", "The All Pakistan Sarafa Gems and Jewellers Association announces the official daily gold rate, which jewellers across the country use as their reference."),
    ("What’s the difference between the live rate and the Sarafa rate?", "The Sarafa rate is announced by the association, usually once a day. The live rate is our estimate that moves with the international gold price and the dollar rate throughout the day. Jewellers price from the Sarafa rate, so use it for buying and selling."),
    ("How is the live rate calculated?", "We take the live international gold price per ounce, add the usual $20 premium the local market applies, convert it to tola (1 ounce is 31.1035 grams, 1 tola is 11.6638 grams) and multiply by the current dollar rate."),
    ("Why are the Rawalpindi market rates different?", "The Sarafa market table shows the rates one Rawalpindi wholesaler actually trades at. Local rawa gold is not fully 24K, ARY bars carry a brand premium, and the 21K jewellery rate is set by the Rawalpindi Sarafa Association with its own buy-back deductions."),
    ("How many grams are in one tola?", "One tola equals 11.6638 grams. One tola has 12 masha, and one masha has 8 ratti."),
    ("What is the nisab for zakat on gold?", "The nisab for gold is 7.5 tola (about 87.48 grams). If you own this much gold or more for a full lunar year, zakat is 2.5% of its value."),
]

def gold_page(path, h1, title, desc, urdu, intro, k, faqs, trail, kw, market_sub, place="Pakistan"):
    title_base = title
    title = title.replace(" – ", f" ({DATE_SHORT}) – ", 1)
    faqs = [(f"What is the {k}K gold rate in {place} today?", answer_text(place, k))] + faqs
    return head(title, desc, path, faqs, kw) + f"""
<body data-page="gold" data-karat="{k}" data-title-base="{e(title_base)}">
{topbar("gold", f"{k}K per tola")}
<main id="top" class="wrap">
  {crumbs(trail) if trail else ""}
  <div class="hero">
    <div class="hero-head">
      <div>
        <h1>{h1}</h1>
        <p class="today" id="todayLine">Live price, official Sarafa rate and international chart</p>
      </div>
      <p class="urdu">{urdu}</p>
    </div>
    <p class="answer">{answer_text(place, k)}</p>
    <div class="hero-grid">
      {live_card(f"Live {k}K gold, per tola")}
      {official_card(k)}
    </div>
    <p class="intro">{intro}</p>
  </div>
  {rates_section("Gold rates by karat", k)}
  {market_section("gold", "Sarafa market rates", market_sub)}
  {intl_section("gold")}
  {calc_section()}
  {UNITS}
  {faq_section(faqs)}
  {links_section(path)}
  {refs_section("gold")}
  {FOOTER}
</main>
{bottomnav("gold")}
{FALLBACK_JS}
<script src="/assets/site.js" defer></script>
</body>
</html>
"""

MARKET_SUB_DEFAULT = "What a Rawalpindi Sarafa Bazar wholesaler is trading at today, for bars, local gold and 21K jewellery."
built = []

# Home
page("/", gold_page(
    "/", "Gold rate today in Pakistan",
    "Gold Rate Today in Pakistan – Live Tola Price, Sarafa Rate & Gold Chart",
    "Live gold rate in Pakistan per tola, 10 gram and gram for 24K, 22K, 21K and 18K, with the official Sarafa rate, Rawalpindi market rates, a live international gold chart and calculators.",
    "آج سونے کا ریٹ",
    "The official rate is set once a day by the Sarafa association. The live rate moves with the world gold price and the dollar, so you can see where the next official rate is heading.",
    24, BASE_FAQ, None,
    "gold rate today in pakistan, gold price per tola, live gold rate pakistan, sarafa rate today, sone ki qeemat", MARKET_SUB_DEFAULT))
built.append(("/", "1.0"))

# Cities
for slug, name, urdu in CITIES:
    path = f"/gold-rate-{slug}/"
    local = slug in ("rawalpindi", "islamabad")
    intro = (f"The gold rate in {name} follows the official rate announced each day by the All Pakistan Sarafa Gems and Jewellers Association, "
             f"so the base price is the same as in the rest of the country. Jewellers in {name} add their own making charges on top.")
    if local:
        intro += f" The Sarafa market table below comes from Rawalpindi’s Sarafa Bazar, which {name}’s jewellery markets follow."
    faqs = [
        (f"Is the gold rate in {name} different from other cities?", f"No. The official Sarafa rate is announced for the whole country, so the base gold price in {name} is the same as in Karachi, Lahore or Islamabad. Making charges and buy-back deductions differ from shop to shop."),
        (f"What is the 21K gold rate in {name} today?", f"The 21K rate is 87.5% of the 24K rate. The rate cards above show today’s 21K price per tola, 10 gram and gram for {name}, using either the live or the official Sarafa rate."),
    ] + BASE_FAQ[:3] + BASE_FAQ[4:]
    market_sub = ("Rates traded today in Rawalpindi’s Sarafa Bazar, which the jewellery markets of Rawalpindi and Islamabad follow."
                  if local else "For comparison: what a Rawalpindi Sarafa Bazar wholesaler is trading at today.")
    page(path, gold_page(
        path, f"Gold rate today in {name}",
        f"Gold Rate Today in {name} – Live Tola Price (24K, 22K, 21K)",
        f"Today’s gold rate in {name} per tola, 10 gram and gram for 24K, 22K, 21K and 18K. Live price, official Sarafa rate, chart and jewellery calculator.",
        f"{urdu} میں آج سونے کا ریٹ", intro, 24, faqs, [(f"Gold rate in {name}", None)],
        f"gold rate in {name.lower()}, gold rate today {name.lower()}, {name.lower()} sarafa rate, gold price {name.lower()} per tola", market_sub, place=name))
    built.append((path, "0.8"))

# Karats
for k in (24, 22, 21, 18):
    path = f"/{k}k-gold-rate/"
    faqs = [
        (f"What is the {k}K gold rate per tola today?", f"The live card at the top shows today’s {k}K gold price per tola, updated every 10 seconds, and the official card shows the Sarafa association’s {k}K rate."),
        (f"How is the {k}K rate calculated?", f"{k}K gold contains {k}/24 parts pure gold, so the {k}K rate is {round(k / 24 * 100, 1)}% of the 24K rate."),
    ] + BASE_FAQ[:3] + BASE_FAQ[4:]
    page(path, gold_page(
        path, f"{k}K gold rate today in Pakistan",
        f"{k}K Gold Rate Today in Pakistan – Per Tola, 10 Gram & Gram",
        f"Live {k}K gold rate in Pakistan per tola, 10 gram and gram, with the official Sarafa rate, chart and a {k}K jewellery calculator.",
        f"{k} قیراط سونے کا ریٹ", KARAT_INFO[k], k, faqs, [(f"{k}K gold rate", None)],
        f"{k}k gold rate pakistan, {k}k gold price per tola, {k} karat gold rate today", MARKET_SUB_DEFAULT))
    built.append((path, "0.8"))

# ---------------------------------------------------------------- silver page
SILVER_FAQ = [
    ("Why is the Pakistani silver rate higher than the international rate?", "Physical silver in Pakistan has traded above the international price since demand surged in 2025. The international value shown here is the world price converted to rupees; the Sarafa market table shows what silver actually trades at."),
    ("What is local (rawa) silver?", "Local silver is silver refined by local workshops from old jewellery or bars. It’s usually a little below 24K purity, which is why it’s cheaper than branded bars."),
    ("How many grams are in one tola of silver?", "One tola is 11.6638 grams, the same for gold and silver."),
    ("What is the nisab for zakat in silver?", "The nisab for silver is 52.5 tola (about 612.36 grams). Many people use the silver nisab when they hold a mix of cash, gold and silver."),
]
path = "/silver-rate/"
page(path, head("Silver Rate Today in Pakistan – Live Per Tola Price & Chart",
                "Live silver rate in Pakistan per tola, 10 gram, gram and kg, with Rawalpindi Sarafa market rates for PSL bars and local silver, and a live international silver chart.",
                path, SILVER_FAQ, "silver rate today in pakistan, chandi ka rate, silver price per tola, psl silver bar rate") + f"""
<body data-page="silver" data-title-base="Silver Rate Today in Pakistan">
{topbar("silver", "Silver per tola")}
<main id="top" class="wrap">
  {crumbs([("Silver rate", None)])}
  <div class="hero">
    <div class="hero-head">
      <div>
        <h1>Silver rate today in Pakistan</h1>
        <p class="today" id="todayLine">Live international value and Sarafa market rates</p>
      </div>
      <p class="urdu">آج چاندی کا ریٹ</p>
    </div>
    <div class="hero-grid">
      {live_card("Silver at international price, per tola", "10 gram", "Market premium")}
      <aside class="official">
        <div class="official-top"><h2>Silver calculator</h2><span class="tag">Chandi</span></div>
        <label for="sw">Weight</label>
        <div class="row">
          <input id="sw" type="number" inputmode="decimal" min="0" step="any" value="10">
          <select id="su" aria-label="Silver weight unit"><option value="tola">Tola</option><option value="gram">Gram</option><option value="kg">Kg</option></select>
        </div>
        <label for="sbasis">Rate</label>
        <select id="sbasis"><option value="intl">International value</option><option value="market">Sarafa market (local silver)</option></select>
        <div class="total num" style="margin-top:14px"><span>Value</span><strong id="sTotal">—</strong></div>
      </aside>
    </div>
    <p class="intro">The international value is the world silver price converted to rupees and updates every 10 seconds. Physical silver in Pakistan usually trades higher, so check the Sarafa market rates below before you buy or sell.</p>
  </div>
  <section id="rates">
    <div class="sec-head"><div>
      <h2 class="sec">Silver rate by weight</h2>
      <p class="sub">At the international price, converted to rupees.</p>
    </div></div>
    <div class="rate-grid num" id="silverGrid"></div>
  </section>
  {market_section("silver", "Sarafa market silver rates", "What a Rawalpindi Sarafa Bazar wholesaler is trading at today, for branded bars and local silver.")}
  {intl_section("silver")}
  {faq_section(SILVER_FAQ)}
  {links_section(path)}
  {refs_section("silver")}
  {FOOTER}
</main>
{bottomnav("silver")}
<script src="/assets/site.js" defer></script>
</body>
</html>
""")
built.append((path, "0.9"))

# ---------------------------------------------------------------- dollar page
DOLLAR_FAQ = [
    ("What is the difference between the interbank and open market dollar rate?", "The interbank rate is what banks trade at with each other. Money changers sell dollars in the open market, usually for a few rupees more. This page shows the interbank rate."),
    ("How often is the dollar rate updated?", "The page checks for a new rate every 30 minutes. The rate source itself refreshes once a day, and the chart shows the market through the day."),
    ("Which currencies are shown?", "The US dollar, Saudi riyal, UAE dirham, British pound, euro and other currencies that matter most to families receiving money from abroad."),
]
path = "/dollar-rate/"
page(path, head("Dollar Rate Today in Pakistan – USD to PKR & Currency Converter",
                "Today’s US dollar rate in Pakistan (USD to PKR), plus riyal, dirham, pound and euro rates, a currency converter and a live chart.",
                path, DOLLAR_FAQ, "dollar rate today in pakistan, usd to pkr, riyal rate, dirham rate, pound rate pakistan") + f"""
<body data-page="dollar" data-title-base="Dollar Rate Today in Pakistan">
{topbar("dollar", "1 USD")}
<main id="top" class="wrap">
  {crumbs([("Dollar rate", None)])}
  <div class="hero">
    <div class="hero-head">
      <div>
        <h1>Dollar rate today in Pakistan</h1>
        <p class="today" id="todayLine">Interbank rate, other currencies and converter</p>
      </div>
      <p class="urdu">آج ڈالر کا ریٹ</p>
    </div>
    <div class="hero-grid">
      <div class="live-card" id="live" aria-live="polite">
        <span class="pill"><span class="dot" id="dot"></span><span id="status">Connecting…</span></span>
        <p class="live-label">1 US dollar in rupees (interbank)</p>
        <p class="live-price num" id="livePrice">—</p>
        <div class="live-foot">
          <span id="liveTime">Checks every 30 minutes</span>
          <button class="btn-ghost" id="refresh" type="button">Refresh now</button>
        </div>
      </div>
      <aside class="official">
        <div class="official-top"><h2>Currency converter</h2><span class="tag">PKR</span></div>
        <label for="cvAmt">Amount</label>
        <input id="cvAmt" type="number" inputmode="decimal" min="0" step="any" value="100">
        <div class="row" style="margin-top:10px">
          <select id="cvCur" aria-label="Currency"><option value="USD">US dollar</option><option value="SAR">Saudi riyal</option><option value="AED">UAE dirham</option><option value="GBP">British pound</option><option value="EUR">Euro</option><option value="CAD">Canadian dollar</option><option value="AUD">Australian dollar</option><option value="QAR">Qatari riyal</option><option value="KWD">Kuwaiti dinar</option><option value="OMR">Omani rial</option><option value="CNY">Chinese yuan</option><option value="MYR">Malaysian ringgit</option></select>
          <select id="cvDir" aria-label="Direction"><option value="toPkr">to rupees</option><option value="fromPkr">rupees to it</option></select>
        </div>
        <div class="total num" style="margin-top:14px"><span>Result</span><strong id="cvOut">—</strong></div>
      </aside>
    </div>
  </div>
  <section id="rates">
    <div class="sec-head"><div>
      <h2 class="sec">Currency rates in Pakistan</h2>
      <p class="sub">Interbank rates in rupees. Money changers usually sell slightly higher.</p>
    </div></div>
    <div class="market"><div class="table-scroll"><table class="mtable fx num">
      <thead><tr><th scope="col">Currency</th><th scope="col">1 unit in PKR</th><th scope="col">Rs 1 buys</th></tr></thead>
      <tbody id="fxBody"><tr><td colspan="3" class="empty">Loading rates…</td></tr></tbody>
    </table></div></div>
  </section>
  {intl_section("dollar")}
  {faq_section(DOLLAR_FAQ)}
  {links_section(path)}
  {refs_section("dollar")}
  {FOOTER}
</main>
{bottomnav("dollar")}
<script src="/assets/site.js" defer></script>
</body>
</html>
""")
built.append((path, "0.9"))

# ---------------------------------------------------------------- daily archive pages
def day_label(iso):
    d = _date.fromisoformat(iso); return f"{d.day} {d.strftime('%B %Y')}", d.strftime("%A")

hist = sorted({h["date"]: h for h in OFFICIAL.get("history", []) if h.get("tola24")}.values(), key=lambda h: h["date"])
for i, h in enumerate(hist):
    path = f"/gold-rate/{h['date']}/"
    label, weekday = day_label(h["date"])
    t24 = h["tola24"]
    prev = hist[i - 1] if i > 0 else None
    nxt = hist[i + 1] if i + 1 < len(hist) else None
    if prev:
        d = t24 - prev["tola24"]
        change = "unchanged from the previous day" if d == 0 else f"{'up' if d > 0 else 'down'} {rs(abs(d))} from {rs(prev['tola24'])} the previous day"
    else:
        change = ""
    ans = (f"On {weekday}, {label}, the official 24K gold rate in Pakistan was {rs(t24)} per tola"
           + (f", {change}" if change else "") + f". 22K was {rs(tola(22, t24))}, 21K was {rs(tola(21, t24))} and 18K was {rs(tola(18, t24))} per tola.")
    faqs = [(f"What was the gold rate in Pakistan on {label}?", ans)]
    nav = '<p class="daynav">' + (f'<a href="/gold-rate/{prev["date"]}/">← {day_label(prev["date"])[0]}</a>' if prev else "<span></span>") + \
          (f'<a href="/gold-rate/{nxt["date"]}/">{day_label(nxt["date"])[0]} →</a>' if nxt else '<a href="/">Today’s live rate →</a>') + "</p>"
    page(path, head(f"Gold Rate in Pakistan on {label} – 24K, 22K, 21K Per Tola",
                    ans[:155], path, faqs, f"gold rate {label.lower()}, gold rate today {label.lower()} pakistan") + f"""
<body data-page="archive">
{topbar("gold", "24K that day").replace('<b id="miniPrice">—</b>', f"<b>{rs(t24)}</b>")}
<main id="top" class="wrap">
  {crumbs([("Gold rate history", "/gold-rate-history/"), (label, None)])}
  <div class="hero">
    <h1>Gold rate in Pakistan on {label}</h1>
    <p class="answer">{ans}</p>
  </div>
  <section>
    <div class="rate-grid num">{static_cards(t24, 21)}</div>
    {nav}
  </section>
  {faq_section(faqs)}
  {links_section(path)}
  {refs_section("gold")}
  <footer><p>Official rates from the All Pakistan Sarafa Gems and Jewellers Association. For today’s rate, see the <a href="/">live gold rate</a>.</p><p>© {OFF_DATE.year} {BRAND}</p></footer>
</main>
{bottomnav("gold").replace('<a href="#international" data-sec="international">', '<a href="/#international">')}
</body>
</html>
""")
    built.append((path, "0.5"))

rows = "".join(
    f'<tr><th scope="row"><a href="/gold-rate/{h["date"]}/">{day_label(h["date"])[0]}</a><small>{day_label(h["date"])[1]}</small></th>'
    f'<td>{rs(h["tola24"])}</td><td>{rs(tola(21, h["tola24"]))}</td></tr>' for h in reversed(hist))
path = "/gold-rate-history/"
page(path, head("Gold Rate History in Pakistan – Daily 24K & 21K Rates Per Tola",
                "Day-by-day official gold rates in Pakistan per tola for 24K and 21K gold, from the All Pakistan Sarafa Gems and Jewellers Association.",
                path, [("Where do these historical rates come from?", "They are the official daily rates issued by the All Pakistan Sarafa Gems and Jewellers Association.")],
                "gold rate history pakistan, gold price history per tola, last week gold rate") + f"""
<body data-page="archive">
{topbar("gold", "Latest 24K").replace('<b id="miniPrice">—</b>', f"<b>{rs(OFFICIAL['tola24'])}</b>")}
<main id="top" class="wrap">
  {crumbs([("Gold rate history", None)])}
  <div class="hero"><h1>Gold rate history in Pakistan</h1>
    <p class="answer">Official daily gold rates per tola, newest first. Tap a date for all karats on that day.</p></div>
  <section>
    <div class="market"><div class="table-scroll"><table class="mtable fx num">
      <thead><tr><th scope="col">Date</th><th scope="col">24K per tola</th><th scope="col">21K per tola</th></tr></thead>
      <tbody>{rows}</tbody></table></div></div>
  </section>
  {links_section(path)}
  <footer><p>© {OFF_DATE.year} {BRAND}</p></footer>
</main>
{bottomnav("gold").replace('<a href="#international" data-sec="international">', '<a href="/#international">')}
</body>
</html>
""")
built.append((path, "0.7"))

# ---------------------------------------------------------------- sitemap & robots
from datetime import date
today = date.today().isoformat()
urls = "\n".join(f"  <url><loc>{SITE_URL}{p}</loc><lastmod>{today}</lastmod><changefreq>hourly</changefreq><priority>{pr}</priority></url>" for p, pr in built)
open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
print("Built", len(built), "pages")
