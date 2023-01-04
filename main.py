import requests
from multiprocessing import Pool
import re
import cloudscraper
import base64
import lxml
from bs4 import BeautifulSoup


login_hash = "" # must be found in chrome request sniffer

cookies = {
    "PHPSESSID" : "", # ur PHPSESSID cookie value
}







scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'darwin','mobile': True},delay=10)


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.66",
}


def get_achievements(url):
    r = scraper.get(url, headers=headers, cookies=cookies)
    some_achiv_str = re.findall(r"eval\( Base64\.decode\( \"(.*)\" \) \);", r.text)
    if len(some_achiv_str) < 2:
        return []
    decoded_achiv_str = base64.b64decode(some_achiv_str[1]).decode("utf-8")
    enc_achievements = re.findall(r"var some_achiv_str = \"(.*)\";", decoded_achiv_str)
    achievements = base64.b64decode(enc_achievements[0]).decode("utf-8")
    achievements_list = re.findall(r"id: \"(.*)\",\r\nhash: \"(.*)\"", achievements)

    result = []
    for item in achievements_list:
        result.append({"id": item[0], "hash": item[1]})

    return result


def send_achievement(_id, _hash):
    payload = {
        "achiv_id": _id,
        "achiv_hash": _hash,
        "the_login_hash": login_hash,
    }
    r = scraper.post(
        "https://jut.su/engine/ajax/get_achievement.php", data=payload, headers=headers, cookies=cookies
    )
    print(r.text)
    return "ok" in r.text


def get_episodes(category):
    result = []
    r = scraper.get("https://jut.su/{}/".format(category), headers=headers, cookies=cookies)
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find_all(
        "a", attrs={"class": re.compile("short-btn.*video the_hildi.*")}
    ):
        result.append("https://jut.su{}".format(link["href"]))
    return result


def main(anime):
    print(anime)
    episodes = get_episodes(anime)
    print(episodes)
    for episode in episodes:
        items = get_achievements(episode)
        for item in items:
            if send_achievement(item["id"], item["hash"]):
                print(
                    "[+] Successfully completed achievement with ID: {}".format(
                        item["id"]
                    )
                )
            else:
                print(
                    "[-] Error when performing an achievement with ID: {}".format(
                        item["id"]
                    )
                )


if __name__ == "__main__":
    with open('animes.txt','r') as f:
        for line in f:
            line = line.strip()
            main(line)
