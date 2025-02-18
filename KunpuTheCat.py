import json
import webbrowser
from requests_html import HTMLSession
import time

def duckduckgo_search(query):
    session = HTMLSession()
    url = f"https://html.duckduckgo.com/html/?q={query}"
    response = session.get(url)

    if response.status_code == 200:
        links = response.html.xpath('//a[contains(@class, "result__a")]/@href')
        if links:
            first_link = links[0]
            if first_link.startswith("/l/"):
                first_link = "https://duckduckgo.com" + first_link
            return first_link
    return None

# Read package names from JSON file
with open("package_names.json", "r", encoding="utf-8") as file:
    data = json.load(file)

def save_package_names(package_names, filename="package_names.json"):
    with open(filename, "w") as file:
        json.dump({"packages": package_names}, file, indent=4)

# Ensure the JSON contains the correct structure with the "packages" key
if "packages" not in data:
    print("Error: JSON should contain the 'packages' key.")
    exit(1)

# Iterate over each package name in the list
for package_name in data["packages"]:
    query = f"apkpure.com {package_name}"
    first_result = duckduckgo_search(query)

    if first_result:
        download_url = first_result + "/downloading"
        print(f"Opening download link for {package_name}: {download_url}")
        webbrowser.open(download_url) 
        time.sleep(1) 

        # Remove the package name from the list after it's processed
        data["packages"].remove(package_name)
        save_package_names(data["packages"])

    else:
        print(f"No result found for {package_name}.")
