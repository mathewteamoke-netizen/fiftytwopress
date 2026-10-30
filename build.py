#!/usr/bin/env python3
"""Generate the static Fifty Two Press site (index + four diary pages)."""
import os, html, json

OUT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://fiftytwopress.com"
EMAIL = "hello@fiftytwopress.com"
PIXEL_ID = "2242132119684786"          # Meta Pixel ID from Events Manager; empty = no pixel
SIGNUP_ACTION = "https://fiftytwopress.us20.list-manage.com/subscribe/post?u=a4008603987d48d43a3424541&id=0001148300&f_id=007166e0f0"     # Mailchimp/Beehiiv form action URL; empty = mailto fallback
SIGNUP_FIELD = "EMAIL" # field name the list expects (Mailchimp: EMAIL)
TAG = "fiftytwopress-22"  # Amazon Associates tracking id, e.g. fiftytwopress-22
AMZ = "https://www.amazon.com.au/dp/"
# Amazon stores where KDP hardcovers are sold. tag = Associates id for that store (only AU joined so far).
STORES = [
    dict(code="AU", label="Australia", domain="amazon.com.au", tag="fiftytwopress-22", cur="AUD"),
    dict(code="US", label="United States", domain="amazon.com", tag="fiftytwopress-20", cur="USD"),
    dict(code="GB", label="United Kingdom", domain="amazon.co.uk", tag="", cur="GBP"),
    dict(code="CA", label="Canada", domain="amazon.ca", tag="", cur="CAD"),
    dict(code="DE", label="Germany", domain="amazon.de", tag="", cur="EUR"),
    dict(code="FR", label="France", domain="amazon.fr", tag="", cur="EUR"),
    dict(code="IT", label="Italy", domain="amazon.it", tag="", cur="EUR"),
    dict(code="ES", label="Spain", domain="amazon.es", tag="", cur="EUR"),
    dict(code="NL", label="Netherlands", domain="amazon.nl", tag="", cur="EUR"),
    dict(code="JP", label="Japan", domain="amazon.co.jp", tag="", cur="JPY"),
]
# List price per store, per diary slug. Fill from KDP > Pricing. Missing = "See price on Amazon".
PRICES = {
    # "executive": {"US": "$49.99", "GB": "£39.99", "DE": "€44.99"},
}

TIERS = [
    dict(slug="executive", short="Executive", n=1, colour="Emerald", cover="#0E3A2A", title="The Executive Diary",
         who="For the person carrying the whole operation.", price="$39.99",
         asin="B0HNHPQP2W",
         why="You answer for everything and everyone. This one gives the week a shape before the week gives you one.",
         blurb="A 52-week planner built for people who carry the whole operation. Each week gives you a planning spread for the three priorities that will make the biggest impact, a colouring panel to switch your head off for ten minutes, and a green-to-red stress score so you can see your mental load before it becomes a problem."),
    dict(slug="manager", short="Manager", n=2, colour="Navy", cover="#0B1A3A", title="The Manager's Diary",
         who="For running a department, a project or a crew of leaders.", price="$34.99",
         asin="B0HNFW9PZN",
         why="Meetings above, people below. The weekly spread keeps both in view; the score tells you which one is winning.",
         blurb="For the person running a department, a project or a crew of leaders. A full weekly planning spread, a colouring panel to reset between the meetings, and a green-to-red stress score that tells you when the week got away from you."),
    dict(slug="team-leader", short="Team Leader", n=3, colour="Burgundy", cover="#3A0E16", title="The Team Leader's Diary",
         who="For the first step into leading people.", price="$29.99",
         asin="B0HNHRTV7S",
         why="Pressure from both directions and no manual. Learn your own pattern early, before it becomes a habit.",
         blurb="For the first step into leading people, where the pressure comes from both directions. A weekly planning spread, a colouring panel for the end of a long shift, and a green-to-red stress score so you learn your own pattern early."),
    dict(slug="professional", short="Professional", n=4, colour="Charcoal", cover="#1A1B1E", title="The Professional's Diary",
         who="For serious work without a team to hide behind.", price="$29.99",
         asin="B0HNHY7XWJ",
         why="Nobody is checking in on you but you. The score makes that check-in a two-minute habit.",
         blurb="For anyone doing serious work without a team to hide behind. A weekly planning spread, a colouring panel to put the day down, and a green-to-red stress score that keeps you honest about how you're really travelling."),
]

WHY_AMAZON = ("Every edition is printed to order by Amazon: hardcover, full-colour pages, bound fresh for each copy and "
              "shipped from the facility nearest you. The button takes you to Amazon to check out, with Amazon delivery and returns.")

FAQS = [
    ("Why do I order on Amazon?", WHY_AMAZON + " We earn a small commission on top of our royalty, at no cost to you."),
    ("Which tier is mine?", "The book inside is the same in all four. Pick by the job. Executive: you carry the whole operation. Manager: you run a department or project. Team Leader: your first step into leading people. Professional: serious work, no team to hide behind."),
    ("Is it dated?", "No. All 52 weeks are undated, so you can start any Monday and skip nothing if you take a week off."),
    ("Do I need to be good at colouring?", "No. The panels are simple line work. Ten minutes with any pen is the point, not the result. The research on colouring and anxiety used ordinary pencils and structured patterns, which is what these are."),
    ("Does colouring really reduce stress?", "Studies with adults have found that short sessions of structured colouring lower reported anxiety, and that a week of daily colouring reduced anxiety and depressive symptoms. It is not a treatment, but it is a reliable way to bring the dial down at the end of a hard day."),
    ("Where does it ship?", "Australia, the United States, Canada, the United Kingdom, Europe and Japan. Pick your Amazon store at the top of the page and every Order button goes to that store. Australian orders of the hardcover are shipped from Amazon's European print facility, so allow around two weeks."),
]

E = html.escape
def amz(t):
    return AMZ + t['asin'] + (f"?tag={TAG}" if TAG else "")
def price_html(t, size=None):
    st = f' style="font-size:{size}px"' if size else ""
    return f'<span class="price" data-price="{t["slug"]}"{st}>Price on Amazon</span>'
def buy(t, cls, label="Order on Amazon"):
    return f'<a href="{amz(t)}" class="{cls} buy" data-asin="{t["asin"]}" rel="sponsored noopener" target="_blank">{label}</a>'
def store_select(big=False):
    items = "".join(f'<li role="option" data-code="{x["code"]}" aria-selected="false"><img src="/assets/flags/{x["code"].lower()}.svg" alt="" width="20" height="15"><span>{x["label"]}</span><small>{x["domain"]}</small></li>' for x in STORES)
    cls = "storepick big" if big else "storepick"
    label = '<span class="eyebrow">Your Amazon store</span>' if big else '<span class="sp-label">Amazon store</span>'
    return f'''<div class="{cls}">{label}<button type="button" class="sp-btn" aria-haspopup="listbox" aria-expanded="false"><img class="sp-flag" src="/assets/flags/au.svg" alt="" width="20" height="15"><span class="sp-name">Australia</span><svg width="12" height="8" viewBox="0 0 12 8" aria-hidden="true"><path d="M1 1l5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></button><ul class="sp-list" role="listbox" aria-label="Choose your Amazon store" hidden>{items}</ul></div>'''
def store_json():
    return json.dumps({"stores": STORES, "prices": PRICES}, separators=(",", ":"))

MARK = '''<svg width="{s}" height="{s}" viewBox="0 0 100 100" aria-hidden="true"><rect x="3" y="3" width="94" height="94" fill="none" stroke="currentColor" stroke-width="2.5"/><rect x="9" y="9" width="82" height="82" fill="none" stroke="currentColor" stroke-width="1"/><path d="M9 17V9h8M83 9h8v8M91 83v8h-8M17 91H9v-8" fill="none" stroke="currentColor" stroke-width="2.5"/><text x="50" y="64" text-anchor="middle" font-family="Cormorant Garamond, serif" font-weight="700" font-size="46" letter-spacing="-1" fill="currentColor">52</text><path d="M34 74h32" stroke="currentColor" stroke-width="1.2"/></svg>'''

def lockup(light=False, size=40):
    return f'''<span class="brand"{' style="color:#fff"' if light else ''}><span style="color:var(--c-gold)">{MARK.format(s=size)}</span><span style="display:flex;flex-direction:column"><span class="brand-name">Fifty Two Press</span><span class="brand-sub">Fifty-two week diaries</span></span></span>'''

def pixel():
    if not PIXEL_ID: return ""
    return ("<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};"
            "if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];"
            "s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');"
            f"fbq('init','{PIXEL_ID}');fbq('track','PageView');</script>"
            f'<noscript><img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id={PIXEL_ID}&ev=PageView&noscript=1"></noscript>')

def header():
    return f'''<header class="hdr"><div class="wrap">
<a href="/" aria-label="Fifty Two Press home">{lockup()}</a>
<nav class="nav" aria-label="Main"><a href="/#series">The series</a><a href="/#inside">Inside</a><a href="/#science">The science</a><a href="/#score">Stress score</a><a href="/#about">About</a></nav>
<a href="/#series" class="cta-shop">Shop the series</a>{store_select()}
</div></header>'''

def footer():
    return f'''<footer class="footer"><div class="wrap grid g4" style="padding-top:64px;padding-bottom:40px;gap:32px">
<div style="display:flex;flex-direction:column;gap:14px">{lockup(light=True)}<span>Hardcover editions, printed to order and shipped by Amazon worldwide.</span></div>
<div style="display:flex;flex-direction:column;gap:10px"><strong>Series</strong><a href="/#series">The Back to Green Series</a><span>More series coming</span></div>
<div style="display:flex;flex-direction:column;gap:10px"><strong>Help</strong><a href="/#faq">How to order</a><a href="/#faq">Which tier is mine?</a><a href="mailto:{EMAIL}">Contact</a><a href="https://www.instagram.com/fiftytwopress" rel="noopener" target="_blank">Instagram</a><a href="https://www.facebook.com/profile.php?id=61587081400000" rel="noopener" target="_blank">Facebook</a></div>
<div style="display:flex;flex-direction:column;gap:10px"><strong>By invitation</strong><span>First word on new editions, before they are listed.</span>
<form action="{SIGNUP_ACTION or ('mailto:'+EMAIL)}" method="{'post' if SIGNUP_ACTION else 'get'}" target="_blank" data-signup style="display:flex;gap:8px;flex-wrap:wrap"><label for="news-email" class="sr-only">Email address</label><input id="news-email" name="{SIGNUP_FIELD if SIGNUP_ACTION else 'subject'}" type="email" class="input" placeholder="you@example.com" required style="flex:1 1 160px;min-height:42px">{'<input type="text" name="b_a4008603987d48d43a3424541_0001148300" tabindex="-1" value="" aria-hidden="true" style="position:absolute;left:-5000px">' if SIGNUP_ACTION else ''}<button type="submit" class="cta-notify" style="min-height:42px;padding:0 18px">Request</button></form></div>
</div><div class="wrap" style="padding-bottom:32px;font-size:13px;opacity:.7">&copy; 2026 Fifty Two Press. As an Amazon Associate we earn from qualifying purchases.</div></footer>'''

def shot(t, cls="cardphoto"):
    return f'<img class="{cls}" src="/assets/photos/flat-{t["slug"]}.jpg" alt="{E(t["title"])}, {t["colour"].lower()} hardcover on a desk in window light" loading="lazy">'

def book(t, depth=None):
    d = f"--d:{depth}px;" if depth else ""
    return f'''<div class="book" style="--cover:{t['cover']};{d}"><div class="bk"><img src="/assets/covers/{t['slug']}.jpg" alt="{E(t['title'])}, {t['colour'].lower()} cover" loading="lazy"><div class="spine" aria-hidden="true"><span>{E(t['title'])}</span></div><div class="back" aria-hidden="true"></div><div class="edge"></div><div class="top"></div><div class="bottom"></div></div><div class="sh"></div></div>'''

def score_box():
    cols = ["#2F7A4E", "#3E8A52", "#6B9A4A", "#9AA83F", "#C2A935", "#D29A2E", "#D4802C", "#CF632C", "#C3442C", "#AE2A2A"]
    btns = "".join(f'<button type="button" aria-label="Score {i+1} of 10" data-c="{c}" aria-pressed="{"true" if i==3 else "false"}"></button>' for i, c in enumerate(cols))
    return f'''<div class="score-box" data-score><div class="score-head"><span>Green</span><span>Red</span></div>
<div role="group" aria-label="Stress score, 1 to 10" class="score-grid">{btns}</div>
<div aria-live="polite" class="verdict" data-verdict>Amber. Watch the drift.</div><p class="muted" data-advice>Pick one thing to drop next week before it picks itself.</p></div>'''

def faq_block():
    return '<div class="faq rv">' + "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in FAQS) + "</div>"

def page(title, desc, path, body, has_buybar=False):
    canon = SITE + path
    return f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:image" content="{SITE}/assets/brand/og.jpg"><meta property="og:url" content="{canon}"><meta property="og:type" content="website"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/brand/favicon.png"><link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,500&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<meta name="theme-color" content="#121315"><meta name="color-scheme" content="dark">
<link rel="preload" as="image" href="/assets/photos/hero.jpg" fetchpriority="high">
<link rel="stylesheet" href="/assets/site.css">{pixel()}</head>
<body><a class="skip" href="#main">Skip to content</a><div class="ftp{' has-buybar' if has_buybar else ''}">{header()}<main id="main">{body}</main>{footer()}</div><script id="store-config" type="application/json">{store_json()}</script><script src="/assets/site.js" defer></script></body></html>'''

def home():
    ex, rest = TIERS[0], TIERS[1:]
    cards = f'''<article class="tier feature rv"><a href="/diaries/{ex['slug']}/" aria-label="{E(ex['title'])}, see details" class="photo-link">{shot(ex)}</a>
<div class="body"><span class="badge">Tier 1 &middot; Emerald</span><h3 class="h3" style="font-size:34px">{E(ex['title'])}</h3><p class="muted">{E(ex['who'])} {E(ex['why'])}</p>
<div class="row" style="border-top:0;padding-top:4px;justify-content:flex-start;gap:20px">{price_html(ex)}{buy(ex,"cta-amazon")}<a href="/diaries/{ex['slug']}/" class="cta-read">Details</a></div><span class="ship">Printed and shipped by Amazon &middot; <span data-storename>amazon.com.au</span></span></div></article>'''
    for t in rest:
        cards += f'''<article class="tier rv"><a href="/diaries/{t['slug']}/" aria-label="{E(t['title'])}, see details" class="photo-link">{shot(t)}</a>
<span class="badge">Tier {t['n']} &middot; {t['colour']}</span><h3 class="h3">{E(t['title'])}</h3><p class="who">{E(t['who'])}</p>
<div class="row">{price_html(t)}{buy(t,"cta-amazon")}</div><span class="ship">Printed and shipped by Amazon &middot; <span data-storename>amazon.com.au</span></span></article>'''
    body = f'''
<section class="hero" aria-labelledby="hero-h"><img src="/assets/photos/hero.jpg" width="1800" height="763" alt="The four Back to Green diaries stacked on an oak desk by a window" fetchpriority="high" decoding="async"><div class="wrap"><div class="hero-panel">
<span class="eyebrow">Fifty Two Press &middot; Hardcover editions</span><h1 id="hero-h" class="h1">Fifty-two weeks. One honest account of a year.</h1>
<p class="lede hero-copy">A diary is the one friend who hears the whole week, the wins and the losses, and keeps every word to itself. It waits up for you. It doesn't mind the crossed-out days or the ones you skipped entirely. It takes whatever you bring it: plans, regrets, victories, and the honest colour of how things really went. It holds it all without judgement. Fifty-two weeks of that, and you've written something nobody else could have: a true account of a year, kept by the only person who was there for every moment of it.</p>
<div class="hero-ctas"><a href="#series" class="cta-series">Shop the series</a><a href="#score" class="cta-score">Try the stress score</a></div></div></div></section>

<section id="series" class="sec" aria-labelledby="series-h"><div class="wrap">
<div class="rv" style="max-width:720px"><span class="eyebrow">The Back to Green Series</span><h2 id="series-h" class="h2">Four tiers. One idea: get back to green.</h2>
<p class="lede">Hardcover, full-colour, printed to order. Four tiers for four kinds of responsibility; the same system inside every one.</p></div>
<div class="order-bar rv">{store_select(big=True)}<p>Every edition is printed to order by Amazon and shipped from the facility nearest you. Choose your store; prices and Order buttons follow, and you check out on Amazon with its delivery and returns.</p></div>
<div class="grid g3" style="margin-top:48px">{cards}</div>
<div class="rv" style="margin-top:64px;max-width:720px"><span class="eyebrow">Which tier is mine?</span><h3 class="h3" style="font-size:28px;margin-top:10px">Same book inside. The tier is who you answer for.</h3></div>
<div class="tbl-wrap rv"><table class="compare">
<thead><tr><th></th>{"".join(f'<th><a href="/diaries/{t["slug"]}/"><span class="sw" style="background:{t["cover"]}"></span>{t["short"]}</a></th>' for t in TIERS)}</tr></thead>
<tbody>
<tr><th>Made for</th>{"".join(f'<td>{t["who"]}</td>' for t in TIERS)}</tr>
<tr><th>Cover</th>{"".join(f'<td>{t["colour"]}</td>' for t in TIERS)}</tr>
<tr><th>Weeks</th><td>52, undated</td><td>52, undated</td><td>52, undated</td><td>52, undated</td></tr>
<tr><th>Daily colouring</th><td>One panel a day</td><td>One panel a day</td><td>One panel a day</td><td>One panel a day</td></tr>
<tr><th>Stress score</th><td>Green to red, daily</td><td>Green to red, daily</td><td>Green to red, daily</td><td>Green to red, daily</td></tr>
<tr><th>Check-ins</th><td>4 quarterly + year review</td><td>4 quarterly + year review</td><td>4 quarterly + year review</td><td>4 quarterly + year review</td></tr>
<tr><th>Format</th><td>Hardcover, 8.25 &times; 11 in</td><td>Hardcover, 8.25 &times; 11 in</td><td>Hardcover, 8.25 &times; 11 in</td><td>Hardcover, 8.25 &times; 11 in</td></tr>
<tr><th></th>{"".join(f'<td>{buy(t, 'cta-amazon', 'Order')}</td>' for t in TIERS)}</tr>
</tbody></table></div></div></section>

<section id="inside" class="sec dark" aria-labelledby="inside-h"><div class="wrap">
<div class="rv" style="max-width:720px"><span class="eyebrow">Inside every diary</span><h2 id="inside-h" class="h2">Plan it. Colour it. Score it.</h2><p class="lede">A weekly system for a clear head: the few priorities that matter most, ten minutes of colouring to bring your stress level down, and an honest score so you can see your mental load before it tips. 124 pages. 52 undated weeks. Four quarterly check-ins.</p></div>
<div class="bento rv" style="margin-top:40px">
<figure class="wide"><img src="/assets/photos/spread.jpg" alt="Weekly planning spread with seven days, three priorities and a stress score strip" loading="lazy"><figcaption>1 &middot; Plan: three big-hitter priorities, one day at a time</figcaption></figure>
<figure class="tall"><img src="/assets/photos/flat-executive.jpg" alt="The Executive Diary on a desk with a pencil" loading="lazy"><figcaption>Desk size, lies flat</figcaption></figure>
<figure><img src="/assets/photos/panel.jpg" alt="Art deco colouring panel partly coloured in green pencil" loading="lazy"><figcaption>2 &middot; Colour: ten minutes that lower the stress dial</figcaption></figure>
<figure><img src="/assets/photos/quarter.jpg" alt="Quarterly review page with thirteen weeks of green to red scores" loading="lazy"><figcaption>3 &middot; Score: track your stress level, green to red</figcaption></figure>
</div></div></section>


<section id="life" class="sec" aria-labelledby="life-h"><div class="wrap">
<div class="rv" style="max-width:720px"><span class="eyebrow">In the wild</span><h2 id="life-h" class="h2">Wherever the week happens.</h2></div>
<div class="grid g4 life rv" style="margin-top:40px">
<figure><img src="/assets/photos/life-desk.jpg" width="1080" height="1341" alt="Man at a desk holding the Executive Diary" loading="lazy"><figcaption><strong>At the desk</strong>Monday morning, three priorities, before the phone starts.</figcaption></figure>
<figure><img src="/assets/photos/life-kitchen.jpg" width="1080" height="1341" alt="Man writing in the Manager's Diary at a kitchen bench" loading="lazy"><figcaption><strong>At home</strong>Ten minutes at the bench with a coffee and a pencil.</figcaption></figure>
<figure><img src="/assets/photos/life-hotel.jpg" width="1080" height="1341" alt="Man writing in the Professional's Diary at a hotel desk" loading="lazy"><figcaption><strong>Away for work</strong>Hotel desk, phone face-down, ten minutes with the pencil.</figcaption></figure>
<figure><img src="/assets/photos/life-airport.jpg" width="1080" height="1341" alt="Man in an airport lounge with the Team Leader's Diary" loading="lazy"><figcaption><strong>In transit</strong>The week in the book before the flight home.</figcaption></figure>
</div></div></section>

<section id="science" class="sec" aria-labelledby="sci-h"><div class="wrap">
<div class="rv" style="max-width:760px"><span class="eyebrow">The science</span><h2 id="sci-h" class="h2">Why it works.</h2>
<p class="lede">None of this is a gimmick. Each part of the diary leans on published research into stress, attention and mental health.</p></div>
<div class="grid g3" style="margin-top:40px">
<div class="card rv"><span class="num">1</span><span class="eyebrow">Colouring and stress</span><h3 class="h3">Ten minutes of colouring lowers anxiety.</h3><p>In a controlled study, adults who coloured a structured pattern for a short session reported significantly lower anxiety than those who drew freely (Curry and Kasser, 2005). A later trial found that a week of daily colouring reduced symptoms of anxiety and depression in adults (Flett et al., 2017). The panels in every diary are built for exactly that: structured, repetitive, no screen.</p></div>
<div class="card rv"><span class="num">2</span><span class="eyebrow">Priorities and mental load</span><h3 class="h3">Write the plan, quiet the mind.</h3><p>Unfinished tasks keep nagging at your attention, a pattern psychologists call the Zeigarnik effect. Research shows that simply writing a concrete plan for those tasks switches the nagging off, even before you do them (Masicampo and Baumeister, 2011). When the week is too big, the spread asks for three big hitters, the priorities with the most impact, and one day at a time.</p></div>
<div class="card rv"><span class="num">3</span><span class="eyebrow">Tracking stress</span><h3 class="h3">You can only manage what you can see.</h3><p>Putting feelings into words and onto paper is linked with better wellbeing and fewer intrusive thoughts (Pennebaker and Beall, 1986, and decades of expressive-writing studies since). The green-to-red score takes two seconds a day and gives you thirteen weeks of data at every quarterly check-in: your stress levels as a pattern, not a feeling.</p></div>
</div>
<p class="muted rv" style="margin-top:24px;font-size:14px;max-width:760px">Fifty Two Press diaries are a planning and wellbeing tool, not a medical treatment. If your stress or mental health is affecting your life, talk to a doctor or a qualified professional.</p>
</div></section>

<section id="score" class="sec" aria-labelledby="score-h"><div class="wrap split">
<div class="rv"><span class="eyebrow">The stress score</span><h2 id="score-h" class="h2">What is your stress level, really?</h2>
<p class="lede">Pick a colour. This strip sits at the foot of every weekly spread. Two seconds a day, and the most honest reading of your mental health in the book.</p>
<p class="lede">Thirteen weeks later the quarterly check-in turns those colours into a pattern you can plan against: what kept you in the green, what pushed you into the red, what changes next.</p></div>
<div class="rv">{score_box()}</div></div></section>

<section id="about" class="sec" aria-labelledby="about-h" style="background:var(--c-soft)"><div class="wrap split">
<figure class="photo rv"><img src="/assets/photos/founder-ute.jpg" width="1080" height="1341" alt="The founder of Fifty Two Press at the end of a shift, holding the Team Leader's Diary" decoding="async"></figure>
<div class="rv"><span class="eyebrow">About the press</span><h2 id="about-h" class="h2">Made by someone who needed one.</h2>
<p class="lede">Fifty Two Press started on a construction site. The planners on the shelf were corporate and joyless, or pretty and useless. None of them asked the only question that mattered: how are you actually travelling? So we made one that does.</p>
<div class="author author-card"><img class="author-photo" src="/assets/photos/author.jpg" width="1080" height="1341" alt="Mr Capital T" loading="lazy" decoding="async"><div><span class="eyebrow">About the author</span><h3 class="h3">Mr Capital T</h3><p>Mr Capital T is the pen name of the founder of Fifty Two Press. He wrote the Back to Green Series for people whose weeks run flat out: a diary that plans the week, gives you ten minutes with a pencil, and tells you the truth about how you went. More series are on the way.</p></div></div>
</div></div></section>

<section id="faq" class="sec" aria-labelledby="faq-h"><div class="wrap">
<div class="rv" style="max-width:720px"><span class="eyebrow">Questions</span><h2 id="faq-h" class="h2">Before you order.</h2></div>
{faq_block()}</div></section>'''
    return page("Fifty Two Press | Fifty-two weeks. One honest account of a year.",
                "Hardcover fifty-two week diaries with a colouring panel and a green-to-red stress score. The Back to Green Series, printed to order and shipped by Amazon worldwide.",
                "/", body)

def diary(t):
    others = [o for o in TIERS if o["slug"] != t["slug"]]
    oth = "".join(f'''<article class="tier rv"><a href="/diaries/{o['slug']}/" aria-label="{E(o['title'])}, see details" class="photo-link">{shot(o)}</a>
<span class="badge">Tier {o['n']} &middot; {o['colour']}</span><h3 class="h3">{E(o['title'])}</h3><p class="who">{E(o['who'])}</p>
<div class="row">{price_html(o)}<a href="/diaries/{o['slug']}/" class="cta-read">Details</a></div></article>''' for o in others)
    body = f'''
<section class="sec" style="padding-top:32px"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/#series">The Back to Green Series</a><span aria-hidden="true">/</span><span aria-current="page">{E(t['title'])}</span></nav>
<div class="split pdp" style="margin-top:28px;align-items:flex-start">
<div class="gallery"><figure><img src="/assets/photos/flat-{t['slug']}.jpg" alt="{E(t['title'])} on a desk with a pencil"></figure>
<figure><img src="/assets/photos/stack.jpg" alt="The four Back to Green diaries stacked by a window" loading="lazy"></figure>
<figure><img src="/assets/photos/spread.jpg" alt="The weekly planning spread" loading="lazy"></figure></div>
<div class="buycol" style="display:flex;flex-direction:column;gap:18px">
<span class="badge">Tier {t['n']} &middot; {t['colour']} &middot; The Back to Green Series</span>
<h1 class="h1" style="font-size:clamp(36px,4.6vw,58px)">{E(t['title'])}</h1><span class="byline">by Mr Capital T &middot; Fifty Two Press</span>
<p class="lede" style="margin-top:0">{E(t['who'])}</p>
<div style="font-size:30px">{price_html(t,30)}</div>
<div style="display:flex;gap:10px;flex-wrap:wrap">{buy(t,"cta-amazon-big")}</div>
<p class="muted" style="font-size:15px">Printed by Amazon. Their print-on-demand is the only way we can offer hardcover and full-colour pages at this price, so you check out on Amazon with their delivery, returns and Prime shipping. Opens in a new tab.</p>
<p>{E(t['blurb'])}</p>
<dl class="spec"><div><dt>Format</dt><dd>Hardcover, full-colour pages</dd></div><div><dt>Pages</dt><dd>124</dd></div><div><dt>Weeks</dt><dd>52, undated</dd></div><div><dt>Check-ins</dt><dd>4 quarterly reviews</dd></div><div><dt>Colouring</dt><dd>One panel every day</dd></div><div><dt>Stress score</dt><dd>Green to red, daily</dd></div></dl>
</div></div></div></section>

<section class="sec dark" aria-labelledby="pin-h"><div class="wrap"><div class="rv" style="max-width:720px"><span class="eyebrow">Inside</span><h2 id="pin-h" class="h2">Three pages you will live in.</h2></div>
<div class="bento rv" style="margin-top:40px;grid-auto-rows:300px">
<figure><img src="/assets/photos/spread.jpg" alt="Weekly planning spread" loading="lazy"><figcaption>The weekly spread</figcaption></figure>
<figure><img src="/assets/photos/panel.jpg" alt="Colouring panel" loading="lazy"><figcaption>The colouring panel</figcaption></figure>
<figure><img src="/assets/photos/quarter.jpg" alt="Quarterly review page" loading="lazy"><figcaption>The quarterly check-in</figcaption></figure>
</div></div></section>

<section class="sec" aria-labelledby="ps-h"><div class="wrap split"><div class="rv"><span class="eyebrow">Try it</span><h2 id="ps-h" class="h2">Score this week.</h2><p class="lede">{E(t['why'])}</p></div><div class="rv">{score_box()}</div></div></section>

<section class="sec" aria-labelledby="oth-h" style="background:var(--c-soft)"><div class="wrap"><div class="rv"><span class="eyebrow">The rest of the series</span><h2 id="oth-h" class="h2">Same book. Different week.</h2></div>
<div class="grid g3" style="margin-top:40px">{oth}</div></div></section>
<div class="buybar" aria-label="Buy">{price_html(t)}{buy(t,"cta-amazon-big")}</div>'''
    return page(f"{t['title']} | Fifty Two Press", t["blurb"], f"/diaries/{t['slug']}/", body, has_buybar=True)

def write(path, s):
    p = os.path.join(OUT, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(s)

write("index.html", home())
for t in TIERS:
    write(f"diaries/{t['slug']}/index.html", diary(t))
write("404.html", page("Page not found | Fifty Two Press", "That page does not exist.", "/404.html",
      '<section class="sec center"><div class="wrap"><h1 class="h1">Page not found.</h1><p class="lede" style="margin-inline:auto">Try the <a href="/" style="text-decoration:underline">home page</a>.</p></div></section>'))
write("CNAME", "fiftytwopress.com\n")
write(".nojekyll", "")
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
urls = ["/"] + [f"/diaries/{t['slug']}/" for t in TIERS]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{SITE}{u}</loc></url>" for u in urls) + "</urlset>\n")
print("built", len(TIERS) + 2, "pages")
