import requests
import bs4 as bs


# Scrape ids from docs
url = 'https://gogapidocs.readthedocs.io/en/latest/gameslist.html?highlight=list%20games#game-id-list'
site = requests.get(url)

# use bs4 to parse
doc = bs.BeautifulSoup(site.text, "html.parser")

# filter only ids using css
td_results = doc.select("tr.row-odd td:nth-child(2)")
title_list = [td.get_text(strip=True) for td in td_results]

with open("game_ids.txt", mode='w', encoding='utf-8') as f:
    f.write('\n'.join(title_list))


