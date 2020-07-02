from letterboxd_api_interface import LetterboxdAPIInterface
from film import Film
import urllib.request
from bs4 import BeautifulSoup

class LetterboxdScraper(LetterboxdAPIInterface):
    def __init__(self, ds):
        self._build_watchlist_url = lambda user_id : f"https://letterboxd.com/{user_id}/watchlist"
        super().__init__(ds)

    def get_watchlist_films_for_user(self, user_id, bypass_data_store=False):        
        page = self._fetch_url(self._build_watchlist_url(user_id))
        soup = BeautifulSoup(page, 'html.parser')
        num_pages = int(soup.find_all('li', class_="paginate-page")[-1].find('a').text)
        films_index = {}

        # TODO async await
        for page_num in range(num_pages):
            url = self._build_watchlist_url(user_id)

            if (page_num != 0):
                url += f"/page/{page_num}/"

            page = self._fetch_url(url)

            soup = BeautifulSoup(page, 'html.parser')

            film_divs = soup.find_all('div', class_="film-poster")
            for film_div in film_divs:
                new_film = Film({
                    'id' : film_div.get('data-film-slug'),
                    'name' : film_div.find('img').get('alt'),
                })

                new_film.save(self.ds)
                films_index[new_film.id] = new_film.name
            

        return films_index

    def _fetch_url(self, url):
        def fetch_source():
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36","X-Requested-With": "XMLHttpRequest"})
            return urllib.request.urlopen(req).read()

        return self.ds.get( 'requests', url, fetch_source )
