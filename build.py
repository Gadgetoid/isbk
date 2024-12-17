import requests
import pathlib
import json
import time
import sys
from bs4 import BeautifulSoup


HTML_URL = "https://prototypist.net/products/"
JSON_URL = "https://prototypist.net/collections/in-stock-keycap-sets/products.json?page="
TRACKING = "?utm_source=instockbasekits&utm_medium=website&utm_campaign=instockwalletkiller"
FETCH_DELAY = 0.5

INT_KITS = ("International")

OUTPUT_FILE = "index.html"

CACHE_DIR = pathlib.Path("cache")

PRODUCT_PROCESS_CACHE = CACHE_DIR / "proc.json"

CACHE_DIR.mkdir(exist_ok=True)

TEMPLATE = """<!DOCTYPE html><html lang="en">
<head>
    <title>Wallet Killer - A list of in-stock base kits on protoTypist.net</title>
    <meta charset="UTF-8">
</head>
<body>
    <header>
        <h1>The Wallet Killer</h1>
        <h2>A list of in-stock base kits at protoTypist</h2>
        <p>This site is not affiliated with protoTypist in any way, accuracy of kits/prices not guaranteed. No commission is earned. It's just a bit o' fun!</p>
        <p>Run by <a href="https://bsky.app/profile/gadgetoid.com">@Gadgetoid</a>. I am sorry for causing you financial ruin. But if you find this useful, please <a href="https://ko-fi.com/gadgetoid">buy me a coffee!</a></p>
        <p><strong>Filters:</strong> <a href="#" id="filter_all">Show All</a> | <a href="#" id="filter_sub100">Under £100</a> | <a href="#" id="filter_sale">On Sale</a>  | <a href="#" id="filter_novelties">With Novelties</a> | <a href="#" id="filter_international">With International</a></p>
    </header>
    <article>
        <output>
    </article>
    <style type="text/css">
        body {
            background:#eee;
            font-family: Sans-serif;
        }
        ul li {
            display: inline-block;
            padding: 5px 15px;
            background-color: #eee;
            border-radius: 5px;
            margin-right: 10px;
        }
        ul li.sale {
            background-color: #fee;
        }
        a, a:visited, a:active, a:hover {
            color:#000;
        }
        h2 a {
            text-decoration:none;
        }
        h2, ul {
            margin: 0;
            padding: 0;
            margin-bottom:5px;
            list-style: none;
        }
        img {
            margin-top:15px;
        }
        article section {
            padding: 20px;
            margin: 20px;
            background: #fff;
        }
        header {
            padding: 20px;
            margin: 20px;
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
    </style>
    <script type="text/javascript">
        'use strict';
        (function() {
            var sets = document.getElementsByTagName("section");
            console.log(sets);

            document.getElementById("filter_all").onclick = function(){
                for (var j = 0; j < sets.length; j++) {
                    sets[j].classList.toggle("hidden", false);
                }
                return false;
            };

            document.getElementById("filter_sub100").onclick = function(){
                for (var j = 0; j < sets.length; j++) {
                    sets[j].classList.toggle("hidden", !sets[j].classList.contains("_sub100"));
                }
                return false;
            };

            document.getElementById("filter_novelties").onclick = function(){
                for (var j = 0; j < sets.length; j++) {
                    sets[j].classList.toggle("hidden", !sets[j].classList.contains("_novelties"));
                }
                return false;
            };

            document.getElementById("filter_international").onclick = function(){
                for (var j = 0; j < sets.length; j++) {
                    sets[j].classList.toggle("hidden", !sets[j].classList.contains("_international"));
                }
                return false;
            };

            document.getElementById("filter_sale").onclick = function(){
                for (var j = 0; j < sets.length; j++) {
                    sets[j].classList.toggle("hidden", !sets[j].classList.contains("_sale"));
                }
                return false;
            };
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


for product in sorted(product_variants):
    variants = product_variants[product]
    details = get_product_by_handle(product)
    ptitle = details["title"].replace("(In Stock) ", "")
    qprint(f"\nProcessing: {ptitle}")
    novelties_text = ""
    int_text = ""
    iso_text = ""

    if variants is True:
        base_kits = [(details["variants"][0]["title"], True)]

    else:
        base_kits = [variant for variant in variants if variant[1] and "Base" in variant[0]]
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
        css_classes = []
        vtitle, vstock = variant
        vdetails = [p for p in details["variants"] if p["title"] == vtitle or p["title"].startswith(vtitle)][0]
        vtitle = vdetails["title"]
        qprint(f"In stock: {vtitle}")
        try:
            vimage = vdetails["featured_image"]["src"]
        except TypeError:
            vimage = details["images"][0]["src"]

        vprice = float(vdetails["price"]) * 1.2

        try:
            vwasprice = float(vdetails["compare_at_price"]) * 1.2
        except TypeError:
            vwasprice = 0

        if vwasprice and vwasprice != vprice:
            status = f"<ul><li class=\"sale\">💰 £{vprice:.0f} (🥳 was: £{vwasprice:.0f})</li>{novelties_text}{int_text}{iso_text}</ul>"
            css_classes.append("_sale")
        else:
            status = f"<ul><li>💰 £{vprice:.0f}</li>{novelties_text}{int_text}{iso_text}</ul>"


        if vprice < 100:
            css_classes.append("_sub100")

        if novelties_text or "Novelties" in vtitle:
            css_classes.append("_novelties")

        if int_text or "International" in vtitle:
            css_classes.append("_international")

        css_classes = " ".join(css_classes)

        output += f"""<section class="{css_classes}"><h2><a href="{HTML_URL}{product}{TRACKING}">
    {ptitle} - {vtitle}</a></h2>
{status}
<a href="{HTML_URL}{product}{TRACKING}">
    <img src="{vimage}" alt="{ptitle} - {vtitle}" style="max-width: 100%;">
</a></section>
"""

open(OUTPUT_FILE, "w").write(TEMPLATE.replace("<output>", output))