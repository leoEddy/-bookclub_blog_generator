import requests
import urllib.parse

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
        #print(data)
        # Extract and deduplicate author names
        names = [a["name"] for a in data.get("authors", [])]
        unique = list(dict.fromkeys(names))

        # Extract the novel’s first sentence, preferring Open Library excerpts
        first_sentence = ""
        excerpts = data.get("excerpts", [])
        if isinstance(excerpts, list):
            for excerpt in excerpts:
                if excerpt.get("first_sentence") and "text" in excerpt:
                    first_sentence = excerpt["text"]
                    break
        # Fallback to the legacy Raw first_sentence fields if no excerpt found
        if not first_sentence:
            raw_fs = data.get("first_sentence") or data.get("first_sentences", "")
            if isinstance(raw_fs, dict):
                first_sentence = raw_fs.get("value", "") or ""
            elif isinstance(raw_fs, list):
                first_sentence = raw_fs[0] if raw_fs else ""
            else:
                first_sentence = raw_fs or ""

        # Fetch the book description from Wikipedia first paragraph
        description = ""
        wiki_api = "https://en.wikipedia.org/w/api.php"
        # Search for the book title
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": data.get("title", ""),
            "format": "json"
        }
        search_resp = requests.get(wiki_api, params=search_params)
        if search_resp.status_code == 200:
            results = search_resp.json().get("query", {}).get("search", [])
            if results:
                page_title = results[0]["title"]
                # Get the extract (intro) for the found page
                extract_params = {
                    "action": "query",
                    "prop": "extracts",
                    "exintro": True,
                    "explaintext": True,
                    "titles": page_title,
                    "format": "json"
                }
                extract_resp = requests.get(wiki_api, params=extract_params)
                if extract_resp.status_code == 200:
                    pages = extract_resp.json().get("query", {}).get("pages", {})
                    for page in pages.values():
                        extract = page.get("extract", "")
                        if extract:
                            description = extract.split("\n")[0]
                            break

        # Attempt to get cover image from Wikipedia page
        cover = ""
        wiki_api = "https://en.wikipedia.org/w/api.php"
        # Search Wikipedia for the book title
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": data.get("title", ""),
            "format": "json"
        }
        search_resp = requests.get(wiki_api, params=search_params)
        if search_resp.status_code == 200:
            results = search_resp.json().get("query", {}).get("search", [])
            if results:
                page_title = results[0]["title"]
                # Fetch the lead image thumbnail
                img_params = {
                    "action": "query",
                    "titles": page_title,
                    "prop": "pageimages",
                    "pithumbsize": 500,
                    "format": "json"
                }
                img_resp = requests.get(wiki_api, params=img_params)
                if img_resp.status_code == 200:
                    pages = img_resp.json().get("query", {}).get("pages", {})
                    for p in pages.values():
                        thumb = p.get("thumbnail", {})
                        if thumb.get("source"):
                            cover = thumb["source"]
                            break
        # Fallback to Open Library generic cover if Wikipedia has none
        if not cover:
            cover = data.get("cover", {}).get("large") or data.get("cover", {}).get("medium") or ""

        return {
            "title": data.get("title", "").title(),
            "authors": unique,
            "first_sentence": first_sentence,
            "cover": cover,
            "description": description
        }