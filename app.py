from flask import Flask, request, send_from_directory
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/search')
def search():
    keywords = request.args.get('keywords', '')

    # Create list of online shops to search
    shops = ["https://www.ebay.co.uk/sch/i.html?_nkw=",
             "https://www.aliexpress.com/wholesale?SearchText="]

    # Create empty list to store results
    results = []

    # Loop through each shop and search for keywords
    for shop in tqdm(shops, desc='Searching Shops', unit='shop'):
        url = shop + keywords
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Find up to 20 product links and image URLs
        count = 0
        for link in soup.find_all("a", href=True):
            if "ebay.co.uk" in link["href"] or "aliexpress.com" in link["href"]:
                img = link.find("img")
                if img is not None and img["src"] != "https://ir.ebaystatic.com/rs/v/fxxj3ttftm5ltcqnto1o4baovyl.png":
                    # Fix AliExpress links
                    if "aliexpress.com" in link["href"]:
                        link["href"] = link["href"].replace("//", "https://")
                        img["src"] = img["src"].replace("//", "https://")
                    if "http:https://ae01.alicdn.com/kf/S4c4cf3670c1f4dc68d48c2003ec2a26cP/3700x3700.png" not in img["src"] and "http:https://sale.aliexpress.com/download_app_guide.htm" not in link["href"]:
                        results.append((link["href"], img["src"]))
                        count += 1
                        if count >= 30:
                            break

            # Stop searching if we have 60 results (30 per shop)
            if len(results) >= 60:
                break

    # Generate HTML code
    html = "<html><head><title>Results</title><style>table, th, td { border: 1px solid black; border-collapse: collapse; } table { max-width: 800px; width: 100%; } td { max-width: 200px; max-height: 100px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }</style></head><body><h1>Results</h1><table>"
    i = 0
    while i < len(results):
        html += "<tr>"
        for j in range(3):
            if i+j < len(results):
                html += "<td><a href='" + results[i+j][0] + "'> <img src='" + results[i+j][1] + "'></a></td>"
        html += "</tr>"
        i += 3
    html += "</table></body></html>"

    # Return the generated HTML
    return html

if __name__ == '__main__':
    app.run(port=5000)
