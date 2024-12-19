import requests
import pathlib
import json
import time
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo


HTML_URL = "https://prototypist.net/products/"
JSON_URL = "https://prototypist.net/collections/in-stock-keycap-sets/products.json?page="
TRACKING = "?utm_source=instockbasekits&utm_medium=website&utm_campaign=instockwalletkiller"
FETCH_DELAY = 0.5

INT_KITS = ("International")

OUTPUT_FILE = "index.html"

CACHE_DIR = pathlib.Path("cache")

FAVS = [l.strip() for l in open("favourites.txt", "r").readlines()]

print(FAVS)

PRODUCT_PROCESS_CACHE = CACHE_DIR / "proc.json"

CACHE_DIR.mkdir(exist_ok=True)

DATE = datetime.now(tz=ZoneInfo("Europe/London"))

TEMPLATE = """<!DOCTYPE html><html lang="en">
<head>
    <title>Wallet Killer - A list of in-stock base kits on protoTypist.net</title>
    <meta http-equiv="content-type" content="text/html;charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1"></meta>
</head>
<body>
    <header>
        <h1>The Wallet Killer</h1>
        <h2>A list of in-stock base kits at protoTypist</h2>
        <p>This site is not affiliated with protoTypist in any way, accuracy of kits/prices not guaranteed. No commission is earned. It's just a bit o' fun!</p>
        <p>Run by <a href="https://bsky.app/profile/gadgetoid.com">@Gadgetoid</a>. I am sorry for causing you financial ruin. But if you find this useful, please <a href="https://ko-fi.com/gadgetoid">buy me a coffee!</a></p>
        <ul id="filters">
            <li class="title">Filters:</li>
            <li class="filter selected" data-filter="_all">⚡ All</li>
            <li class="filter" data-filter="_sub100">💰 &lt;£100</li>
            <li class="filter" data-filter="_sale">🥳 Sale</li>
            <li class="filter" data-filter="_new">⏰ New</li>
            <li class="filter" data-filter="_favourite">💖 Favs</li>
            <li class="filter" data-filter="_novelties">✨ Novelties</li>
            <li class="filter" data-filter="_international">🌎 International</li>
        <ul id="profiles">
            <li class="title">Profiles:</li>
            <profiles>
        </ul>
    </header>
    <article>
        <output>
    </article>
    <footer>
        <p>Nothing to see here! <a href="#">☝️ back tae top wi' ya!</a></p>
        <p>Or... 🥹 ... stay for a <a href="https://ko-fi.com/gadgetoid">coffee?</a></p>
    </footer>
    <style type="text/css">
        body {
            background:#eee;
            font-family: Verdana, Sans-serif;
            line-height: 1.2em;
            margin: 0;
            padding: 2px;
        }
        h1, h2, h3, h4 {
            font-family: Georgia, Serif;
        }
        h1 {
            margin-bottom:0.2em;
        }
        ul li {
            display: inline-block;
            padding: 5px 15px;
            background-color: #fff;
            border-radius: 5px 0 5px 0;
            margin: 0 10px 10px 0;
            font-size: initial;
            line-height: 1.6em;
        }
        #profiles .filter {
            background-color: #f8f8f8;
        }
        ul li.title {
            background: transparent;
            padding: 5px 0;
        }
        article ul li {
            background-color: #eee;
        }
        ul li.sale {
            background-color: #fee;
        }
        .filter {
            cursor:pointer;cursor:hand;
        }
        .filter:hover, .filter.selected, 
        #profiles .filter.selected {background-color: #efe}
        a, a:visited, a:active, a:hover {
            color:#000;
        }
        h2 a {
            text-decoration:none;
            font-weight:normal;
            font-size:1.2em;
            line-height:1.2em;
        }
        header h2 {
            color: #448;
            font-weight:normal;
        }
        h2 span {
            color: #448;
            font-size: 0.8em;
        }
        ul {
            font-size: 0;
            list-style: none;
        }
        article ul {
            margin-top: 20px;
        }
        h2, ul {
            margin: 0;
            padding: 0;
            margin:10px 0;
        }
        img {
            margin-top:15px;
            width: 100%;
            max-width: 100%;
            border-radius: 0 0 0 20px;
            display: block;
            box-shadow: 0px 0px 3px #ddd;
        }
        article section {
            padding: 20px;
            margin: 20px 0;
            background: #fff;
            border-radius: 0 30px 0 30px;
        }
        header, footer {
            padding: 20px;
            margin: 20px 0;
        }
        .hidden {
            display: none;
        }
        @media only screen and (min-width: 1200px) {
            body {
                max-width: 70%;
                margin: 0 auto;
            }
        }
        @media (prefers-color-scheme: dark) {
            body {
                background-color: #000;
                color: #ccc;
            }
            h1 {
                color: #eee;
            }
            header h2, h2 span {
                color: #aae;
            }
            a, a:visited, a:active, a:hover {
                color:#fff;
            }
            ul li, section ul li {
                background-color: #333;
            }
            #profiles .filter {
                background-color: #222;
            }
            article section {
                background-color: #111;
            }
            .filter:hover, .filter.selected, 
            #profiles .filter.selected {
                background-color: #343;
            }
            ul li.sale {
                background-color: #433;
            }
            img {
                box-shadow: 0px 0px 3px #666;
            }
        }
    </style>
    <script type="text/javascript">
        'use strict';
        (function() {
            var sets = document.getElementsByTagName("section");
            var filters = document.getElementsByClassName("filter");
            function filter(event) {
                var filter = this.dataset.filter;
                for (var f = 0; f < filters.length; f++) {
                    filters[f].classList.toggle("selected", false);
                }
                this.classList.toggle("selected", true);
    
                if (filter == "_all") {
                    for (var j = 0; j < sets.length; j++) {
                        sets[j].classList.toggle("hidden", false);
                    }
                } else {
                    for (var j = 0; j < sets.length; j++) {
                        sets[j].classList.toggle("hidden", !sets[j].classList.contains(filter));
                    }
                }
                return false;
            }
            Array.prototype.forEach.call(filters, (item) => {
                item.addEventListener("click", filter);
            });
        })();
    </script>
</body>
</html>"""


def qprint(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


qprint("\nFetching product data and HTML...")


for i in range(1, 10):
    cache = CACHE_DIR / f"cache{i}.json"
    if pathlib.Path(cache).exists():
        j = json.loads(open(cache).read())
    else:
        r = requests.get(url=JSON_URL + str(i))
        j = r.json()
        open(cache, "w").write(json.dumps(j))

    num_products = len(j["products"])
    qprint(f"Fetching {num_products} products...")

    for product in j["products"]:
        url = HTML_URL + product["handle"]
        qprint(url)
        cache = (CACHE_DIR / product["handle"]).with_suffix(".html")
        if cache.exists():
            html = open(cache, "r").read()
        else:
            r = requests.get(url=url)
            open(cache, "w").write(r.text)
            time.sleep(FETCH_DELAY)

qprint("\nLoading product data...")

# Load product data from cache
products = []
for i in range(1, 10):
    cache = CACHE_DIR / f"cache{i}.json"
    if pathlib.Path(cache).exists():
        j = json.loads(open(cache).read())

    products += j["products"]

def get_product_by_handle(handle):
    return [p for p in products if p["handle"] == handle][0]

# Load HTML files from cache
html_files = CACHE_DIR.glob("*.html")
product_variants = {}

qprint("\nProcessing downloaded html files...")

if pathlib.Path(PRODUCT_PROCESS_CACHE).exists():
    product_variants = json.loads(open(PRODUCT_PROCESS_CACHE, "r").read())
else:
    product_variants = {}
    for file in html_files:
        f = pathlib.Path(file)
        product_slug = f.stem
        qprint(f"Parsing {file}")
        soup = BeautifulSoup(open(file, "r").read())
        product_variants[product_slug] = []

        if soup.find("div", attrs={"class": "variant-picker__option-values"}):
            # Product has variants
            variants = soup.find("div", attrs={"class": "variant-picker__option-values"}).find_all("input", attrs={"class": "sr-only", "type": "radio"})

            for variant in variants:
                in_stock_label = variant.find_next("label", attrs={"for": variant.get("id")})
                vtitle = in_stock_label.find_next("span", class_=lambda cls: cls is None or "block-swatch__color" not in cls).contents[0]
                vin_stock = "is-disabled" not in in_stock_label.get("class")
                product_variants[product_slug].append((vtitle, vin_stock))
        else:
            # Probably just a single product
            qprint("SINGLE PRODUCT!!!")
            product_variants[product_slug] = True

    open(PRODUCT_PROCESS_CACHE, "w").write(json.dumps(product_variants))

output = ""
profiles = {}

for product in sorted(product_variants):
    variants = product_variants[product]
    details = get_product_by_handle(product)
    ptitle = details["title"].replace("(In Stock) ", "")
    qprint(f"\nProcessing: {ptitle}")
    novelties_text = ""
    int_text = ""
    iso_text = ""
    profile_text = ""

    pprofile = ""

    def body_has(*choices):
        for choice in choices:
            if choice in details["body_html"]:
                return True
        return False

    # Yes some instances of Cherry profile include a non breaking space...
    if body_has("Cherry profile",
                "Profile: Cherry",
                "cherry profile",
                "Cherry Profile",
                "Cherry Keycap Profile",
                "Keycap Profile: Cherry",
                "CHRRRY Profile",
                "Cherry profile",
                "Cherry-profile",
                "Cherry-like",
                "Keycap Profile - Cherry",
                "Profile : Cherry"):
        pprofile = "Cherry"
    elif body_has("MTNU profile"):
        pprofile = "MTNU"
    elif "KAM " in ptitle or body_has("KAM Profile", "Profile: Keycreative KAM", "KAM uniform keycap profile", "Keyreative KAM PBT dyesub"):
        pprofile = "KAM"
    elif "CXA " in ptitle or body_has("Keycap Profile - CXA", "CXA Profile"):
        pprofile = "CXA"
    elif "SA " in ptitle or body_has("SA profile"):
        pprofile = "SA"
    elif "DCS " in ptitle or body_has("DCS profile", "DCS Profile", "Keycap Profile: DCS"):
        pprofile = "DCS"
    elif body_has("DSS Profile"):
        pprofile = "DSS"
    elif "GMK CYL " in ptitle or body_has("Profile: CYL", "GMK CYL profile"):
        pprofile = "CYL"
    elif "KAT " in ptitle:
        pprofile = "KAT"
    elif "MDA " in ptitle:
        pprofile = "MDA"
    elif "MG " in ptitle:
        pprofile = "MG"
    else:
        pprofile = "Unknown"

    
    if variants is True:
        base_kits = [(details["variants"][0]["title"], True)]

    else:
        # TODO: Bit of a hack for CXA Iara, CXA Sugarplum, Tyche One, etc which have *one* variant that is effectively the base kit
        if len(variants) == 1 and variants[0][1] and "Add-on" not in variants[0][0]:
            base_kits = variants
        else:
            # TODO: The "Blank Kit" here is a hack for MDA Future Suzuri
            # TODO: Extra hack here to remove GMK Hazakura Keycaps - Base (Latin) Kit, GMK CYL Shadow - GMK CYL Shadow - Latin Base, DCS White On Black Alps - DCS WoB Alps - Base and DCS Reaper Keyset - DCS Reaper - Alps Base
            base_kits = [variant for variant in variants if variant[1] and ("Base" in variant[0] or "Blank Kit" in variant[0]) and not "Alps " in variant[0] and not "Latin " in variant[0]]
        if not base_kits:
            qprint("No base kits... skipping!")
            continue

        novelties = [variant for variant in variants if "Novelties" in variant[0] and variant[1]]
        if novelties:
            novelties_text = f"<li>✨ Novelties in stock!</li>"
            qprint("Has Novelties")

        international = [variant for variant in variants if variant[0] in INT_KITS and variant[1]]
        if international:
            int_text = f"<li>🌎 International kit in stock!</li>"
            qprint("Has International Kits")

        iso_kits = [variant[1] for variant in variants if variant[0].startswith("ISO")]
        if iso_kits:
            iso_text = "<li>🇬🇧 Some ISO kits in stock</li>" if True in iso_kits else "<li>⚠️ No ISO kits!</li>"


    for variant in base_kits:
        if pprofile:
            profiles[pprofile] = profiles.get(pprofile, 0) + 1
            profile_text = f"<li>🍒 {pprofile}</li>" if pprofile == "Cherry" else f"<li>⌨️ {pprofile}</li>"

        new_text = ""
        fav_text = ""
        css_classes = []
        vtitle, vstock = variant
        vdetails = [p for p in details["variants"] if p["title"] == vtitle or p["title"].startswith(vtitle)][0]
        vtitle = vdetails["title"]
        vdate = datetime.fromisoformat(vdetails["created_at"])
        vage = abs((DATE - vdate).days)
        qprint(f"In stock: {vtitle}, age: {vage} days")

        if pprofile:
            css_classes.append(f"_profile_{pprofile.lower()}")
        else:
            css_classes.append(f"_profile_none")

        try:
            vimage = vdetails["featured_image"]["src"]
        except TypeError:
            vimage = details["images"][0]["src"]

        vprice = float(vdetails["price"]) * 1.2

        if product in FAVS or f"{product}/{vtitle}" in FAVS:
            css_classes.append("_favourite")
            fav_text = "<li title=\"One of my favourites!\">💖</li>"

        if vage <= 30:
            css_classes.append("_new")
            new_text = "<li title=\"30 days old or less\">⏰ New</li>"

        try:
            vwasprice = float(vdetails["compare_at_price"]) * 1.2
        except TypeError:
            vwasprice = 0

        if vwasprice and vwasprice != vprice:
            status = f"<ul><li class=\"sale\">💰 £{vprice:.0f} <small>(🥳 was: £{vwasprice:.0f})</small></li>{profile_text}{new_text}{fav_text}{novelties_text}{int_text}{iso_text}</ul>"
            css_classes.append("_sale")
        else:
            status = f"<ul><li>💰 £{vprice:.0f}</li>{profile_text}{new_text}{fav_text}{novelties_text}{int_text}{iso_text}</ul>"

        if vprice < 100:
            css_classes.append("_sub100")

        if novelties_text or "Novelties" in vtitle:
            css_classes.append("_novelties")

        if int_text or "International" in vtitle:
            css_classes.append("_international")

        css_classes = " ".join(css_classes)

        pvtitle = f"<span> - {vtitle}</span>" if vtitle != "Default Title" else ""

        output += f"""<section class="{css_classes}"><h2><a href="{HTML_URL}{product}{TRACKING}">
    {ptitle}{pvtitle}</a></h2>
{status}
<a href="{HTML_URL}{product}{TRACKING}">
    <img src="{vimage}" alt="{ptitle} - {vtitle}" loading="lazy">
</a></section>
"""

profiles_html = ""

for profile, count in profiles.items():
    profiles_html += f"<li class=\"filter\" data-filter=\"_profile_{profile.lower()}\">{profile} <small>({count})</small></li>"

open(OUTPUT_FILE, "w").write(TEMPLATE.replace("<output>", output).replace("<profiles>", profiles_html))