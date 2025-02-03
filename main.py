import requests
from bs4 import BeautifulSoup
import os

session: requests.Session = requests.Session()
session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))

game_data: dict[str, dict[str, str]] = {
    "genshin_impact": {
        "name": "Paimon's_Paintings",
        "url": r"https://genshin-impact.fandom.com/wiki/Paimon's_Paintings"
    },
    "honkai_star_rail": {
        "name": "Pom-Pom_Gallery",
        "url": r"https://honkai-star-rail.fandom.com/wiki/Pom-Pom_Gallery"
    },
}

license_text = r"""
{}:
    Community content is available under CC-BY-SA unless otherwise noted. 
"""

def get_html(url: str) -> str:
    return session.get(url).text

def get_image_urls(html: str) -> list[str]:
    return [
        img["src"].split("/revision")[0]
        for table in BeautifulSoup(html, "html.parser").find_all("div", class_="wikia-gallery")
        for img in table.find_all("img")
        if img["src"].startswith("https://static.wikia.nocookie.net")
    ]

def download_image(url: str, path: str) -> None:
    with open(path, "wb") as f:
        f.write(session.get(url).content)

if __name__ == "__main__":
    for game in game_data:
        os.makedirs(game_data[game]["name"], exist_ok=True)
        image_urls: list[str] = get_image_urls(get_html(game_data[game]["url"]))
        with open(f"{game_data[game]['name']}/urls.txt", "w") as f:
            f.write("\n".join(image_urls))
        with open(f"{game_data[game]['name']}/paths.txt", "w") as f:
            f.write(
                "\n".join(
                    f"{game_data[game]['name']}/{url.split('/')[-1]}"
                    for url in image_urls
                )
            )
        with open(f"{game_data[game]['name']}/licenses.txt", "w") as f:
            f.write(
                license_text.format(
                    game_data[game]["url"]
                )
            )
        for url in image_urls:
            download_image(url, f"{game_data[game]['name']}/{url.split('/')[-1]}")


