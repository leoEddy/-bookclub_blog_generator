import requests
import re

class BookFetcher:
    BASE_URL = "https://openlibrary.org/api/books"

    def fetch_by_isbn(self, isbn):
        params = {
            "bibkeys": f"ISBN:{isbn}",
            "format": "json",
            "jscmd": "data"
        }
        resp = requests.get(self.BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json().get(f"ISBN:{isbn}", {})
        # Extract and deduplicate author names
        names = [a["name"] for a in data.get("authors", [])]
        unique = list(dict.fromkeys(names))

        # Attempt to get original publication date from Open Library work data
        orig_pub = ""
        works = data.get("works", [])
        if works and isinstance(works, list):
            work_key = works[0].get("key")
            if work_key:
                work_resp = requests.get(f"https://openlibrary.org{work_key}.json")
                if work_resp.status_code == 200:
                    work_data = work_resp.json()
                    orig_pub = work_data.get("first_publish_date", "") or ""

        # Fallback to edition-level publish_date if still missing
        if not orig_pub:
            orig_pub = data.get("publish_date", "") or ""

        # Fallback to Google Books as last resort
        if not orig_pub:
            gb_params = {"q": f"isbn:{isbn}"}
            gb_resp = requests.get("https://www.googleapis.com/books/v1/volumes", params=gb_params)
            if gb_resp.status_code == 200:
                items = gb_resp.json().get("items", [])
                years = []
                for item in items:
                    pd = item.get("volumeInfo", {}).get("publishedDate", "")
                    match = re.match(r"(\d{4})", pd)
                    if match:
                        years.append(int(match.group(1)))
                if years:
                    orig_pub = str(min(years))
        
        return {
            "title": data.get("title"),
            "authors": unique,
            "original_publication_date": orig_pub,
            "cover": data.get("cover", {}).get("large"),
            "description": data.get("subtitle") or data.get("notes", "")
        }