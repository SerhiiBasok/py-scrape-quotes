import csv
import dataclasses
from dataclasses import astuple, fields

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclasses.dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_product(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[a.text.strip() for a in quote.select("a.tag")],
    )


def get_next_button(soup: BeautifulSoup) -> str | None:
    next_btn = soup.select_one(".next a")
    if next_btn and next_btn.has_attr("href"):
        return BASE_URL + next_btn["href"]
    return None


def get_num_pages(url: BASE_URL) -> int:
    count = 0
    while url:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        count += 1
        url = get_next_button(soup)
    return count


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_product(quote) for quote in quotes]


def get_page_quotes() -> list[Quote]:
    text = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(text, "html.parser")
    num_pages = get_num_pages(BASE_URL)
    all_quotes = get_single_page_quotes(first_page_soup)
    for page_num in range(2, num_pages + 1):
        text = requests.get(BASE_URL, params={"page": page_num}).content
        next_page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(next_page_soup))
    return all_quotes


def write_quotes_to_csv(quotes: [Quote], path: str) -> None:
    with open(path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(path: str = "result.csv") -> None:
    write_quotes_to_csv(get_page_quotes(), path)


if __name__ == "__main__":
    main("result.csv")
