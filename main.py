import requests
from bs4 import BeautifulSoup
import os
import zipfile
session: requests.Session = requests.Session()
session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))

game_data: dict[str, dict[str, str]] = {
    "genshin_impact": {
        "name": "Paimon_s_Paintings",
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

def download_game_stickers(game: str, sub_dir: str = None) -> None:
    sub_dir: str = sub_dir or game_data[game]["name"]
    os.makedirs(sub_dir, exist_ok=True)
    image_urls: list[str] = get_image_urls(get_html(game_data[game]["url"]))
    with open(f"{sub_dir}/urls.txt", "w") as f:
        f.write("\n".join(image_urls))
    with open(f"{sub_dir}/paths.txt", "w") as f:
        f.write(
            "\n".join(
                f"{sub_dir}/{url.split('/')[-1].replace(r'%27', '_')}"
                for url in image_urls
            )
        )
    with open(f"{sub_dir}/licenses.txt", "w") as f:
        f.write(
            license_text.format(
                game_data[game]["url"]
            )
        )
    for url in image_urls:
        download_image(url, f"{sub_dir}/{url.split('/')[-1].replace(r'%27', '_')}")

def export_as_zipfile(sub_dirs: list[str] = None) -> None:
    with zipfile.ZipFile("output.zip", "w") as z:
        for sub_dir in sub_dirs:
            for file in os.listdir(sub_dir):
                z.write(f"{sub_dir}/{file}", f"{sub_dir}/{file.replace(r'%27', '_')}")

if __name__ == "__main__":
    import argparse

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--zipped", default=False, action="store_true", help="Save as a zip file")
    arg_parser.add_argument("--games", 
                            type=str, 
                            nargs="+", 
                            default=["genshin_impact", "honkai_star_rail"], 
                            help="Only download specified games",
                            choices=["genshin_impact", "honkai_star_rail"]
                            )
    args = arg_parser.parse_args()

    for game in args.games:
        download_game_stickers(game)
    
    if args.zipped:
        export_as_zipfile([game_data[game]["name"] for game in args.games])



