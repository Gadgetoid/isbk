import requests
import pathlib
import json
import time
from bs4 import BeautifulSoup


HTML_URL = "https://prototypist.net/products/"
JSON_URL = "https://prototypist.net/collections/in-stock-keycap-sets/products.json?page="
TRACKING = "?utm_source=instockbasekits&utm_medium=website&utm_campaign=instockwalletkiller"

OUTPUT_FILE = "index.html"

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
        a, a:visited, a:active, a:hover {
            color:#000;
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
        @media only screen and (min-width: 1200px) {
            body {
                max-width: 50%;
                margin: 0 auto;
            }
        }
    </style>
</body>
</html>"""

CACHE_DIR = pathlib.Path("cache")

PRODUCT_PROCESS_CACHE = CACHE_DIR / "proc.json"

CACHE_DIR.mkdir(exist_ok=True)


for i in range(1, 10):
    cache = CACHE_DIR / f"cache{i}.json"
    if pathlib.Path(cache).exists():
        j = json.loads(open(cache).read())
    else:
        r = requests.get(url=JSON_URL + str(i))
        j = r.json()
        open(cache, "w").write(json.dumps(j))

    num_products = len(j["products"])
    print("Fetching {num_products} products...")

    for product in j["products"]:
        url = HTML_URL + product["handle"]
        print(url)
        cache = (CACHE_DIR / product["handle"]).with_suffix(".html")
        if cache.exists():
            html = open(cache, "r").read()
        else:
            r = requests.get(url=url)
            open(cache, "w").write(r.text)
            time.sleep(1.0)

INT_KITS = ("International")

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

if pathlib.Path(PRODUCT_PROCESS_CACHE).exists():
    product_variants = json.loads(open(PRODUCT_PROCESS_CACHE, "r").read())
else:
    product_variants = {}
    for file in html_files:
        f = pathlib.Path(file)
        product_slug = f.stem
        print(f"Parsing {file}")
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
            print("SINGLE PRODUCT!!!")
            product_variants[product_slug] = True

    open(PRODUCT_PROCESS_CACHE, "w").write(json.dumps(product_variants))

output = ""

for product, variants in product_variants.items():
    details = get_product_by_handle(product)
    ptitle = details["title"]
    novelties_text = ""
    int_text = ""
    iso_text = ""

    if variants is True:
        base_kits = [(details["variants"][0]["title"], True)]

    else:
        base_kits = [variant for variant in variants if variant[1] and "Base" in variant[0]]
        if not base_kits:
            continue

        novelties = [variant for variant in variants if "Novelties" in variant[0] and variant[1]]
        if novelties:
            novelties_text = f"<li>✨ (Some) Novelties in stock!</li>"

        international = [variant for variant in variants if variant[0] in INT_KITS and variant[1]]
        if international:
            int_text = f"<li>🌎 (Some) International kits in stock!</li>"

        iso_kits = [variant[1] for variant in variants if variant[0].startswith("ISO")]
        if iso_kits:
            iso_text = "<li>🇬🇧 Some ISO kits in stock</li>" if True in iso_kits else "<li>⚠️ No ISO kits!</li>"

    for variant in base_kits:
        vtitle, vstock = variant
        vdetails = [p for p in details["variants"] if p["title"] == vtitle or p["title"].startswith(vtitle)][0]
        vtitle = vdetails["title"]
        try:
            vimage = vdetails["featured_image"]["src"]
        except TypeError:
            vimage = details["images"][0]["src"]

        vprice = float(vdetails["price"]) * 1.2
        status = f"<ul><li>💰 £{vprice:.0f}</li>{novelties_text}{int_text}{iso_text}</ul>"

        ptitle = ptitle.replace("(In Stock) ", "")

        output += f"""<section><h2><a href="{HTML_URL}{product}{TRACKING}">
    {ptitle} - {vtitle}</a></h2>
{status}
<a href="{HTML_URL}{product}{TRACKING}">
    <img src="{vimage}" alt="{ptitle} - {vtitle}" style="max-width: 100%;">
</a></section>
"""

open(OUTPUT_FILE, "w").write(TEMPLATE.replace("<output>", output))