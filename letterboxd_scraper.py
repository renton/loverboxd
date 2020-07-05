from letterboxd_api_interface import LetterboxdAPIInterface
from film import Film
from user import User
import urllib.request
from bs4 import BeautifulSoup

HIGHEST_RATING_TO_USE = 8

class LetterboxdScraper(LetterboxdAPIInterface):
    def __init__(self, ds):
        self._build_user_watchlist_url = lambda user_id : f"https://letterboxd.com/{user_id}/watchlist"
        self._build_user_films_url = lambda user_id : f"https://letterboxd.com/{user_id}/films/by/member-rating"
        self._build_film_ratings_url = lambda film_id : f"https://letterboxd.com/{film_id}/ratings"

        super().__init__(ds)

    def get_films_for_user(self, user_id, highest_rating_to_use=(HIGHEST_RATING_TO_USE+1), bypass_cache=False):
        if not bypass_cache:
            user = self.ds.get('users', user_id)
            if user:
                return user

        rating_index = {}
        encountered_all_ratings = False        

        page = self._fetch_url(self._build_user_films_url(user_id))
        soup = BeautifulSoup(page, 'html.parser')

        paginator = soup.find_all('li', class_="paginate-page")
        if paginator:
            num_pages = int(paginator[-1].find('a').text)
        else:
            num_pages = 1

        # TODO async await
        for page_num in range(num_pages):
            url = self._build_user_films_url(user_id)

            if (page_num != 0):
                url += f"/page/{page_num + 1}/"
                page = self._fetch_url(url)

            soup = BeautifulSoup(page, 'html.parser')

            film_lis = soup.find_all('li', class_="poster-container")
            for film_li in film_lis:
                film_id = film_li.find('div', class_="film-poster").get('data-film-slug')

                rating_span = film_li.find('span', class_="rating")
                if rating_span:
                    rating = int(rating_span.get('class')[-1].split('-')[-1])
                else:
                    rating = None

                if rating and (page_num >= (num_pages / 3)) and rating == 10:
                    # This user gives too many 10s. Ignore
                    print('-> Too many 10s : skipping ', user_id)
                    rating_index = {}
                    encountered_all_ratings = True                    
                    break

                if ( highest_rating_to_use != None ) and ( ( rating is None ) or ( rating < highest_rating_to_use ) ):
                    encountered_all_ratings = True
                    break

                id = f"{user_id}:{film_id}"
                new_watch = {
                    'id'      : id,
                    'film_id' : film_id,
                    'user_id' : user_id,
                    'rating'  : rating,
                }

                rating_index[film_id] = new_watch

            if encountered_all_ratings:
                break

        new_user = User( { 'id' : user_id, 'watched_films' : rating_index } )
        new_user.save(self.ds)

        return rating_index
    
    def get_ratings_for_film(self, film_id, highest_rating_to_use=(HIGHEST_RATING_TO_USE+1), bypass_cache=False):
        if not bypass_cache:
            film = self.ds.get('films', film_id)

            if film:
                return film

        # TODO pagination
        encountered_all_ratings = False        
        rating_index = {}
        page = self._fetch_url(self._build_film_ratings_url(film_id))
        soup = BeautifulSoup(page, 'html.parser')

        rating_groups = soup.find_all('section', class_="film-rating-group")
        for rating_group in rating_groups:
            rating_span = rating_group.find('span', class_="rating")
            if rating_span:
                rating = int(rating_span.get('class')[-1].split('-')[-1])
            else:
                rating = None

            if ( highest_rating_to_use != None ) and ( ( rating is None ) or ( rating < highest_rating_to_use ) ):
                encountered_all_ratings = True
                break

            users = rating_group.find_all('a', class_="avatar")
            for user in users:
                user_id = user.get('href')[1:-1]
                id = f"{user_id}:{film_id}"
                new_watch = {
                    'id'      : id,
                    'film_id' : film_id,
                    'user_id' : user_id,
                    'rating'  : rating,
                }

                rating_index[user_id] = new_watch

            if encountered_all_ratings:
                break

        new_film = Film( { 'id' : film_id, 'user_watches' : rating_index } )
        new_film.save(self.ds)

        #TODO save film to DS
        return rating_index

    def get_watchlist_films_for_user(self, user_id, bypass_data_store=False):        
        page = self._fetch_url(self._build_user_watchlist_url(user_id))
        soup = BeautifulSoup(page, 'html.parser')

        num_pages = int(soup.find_all('li', class_="paginate-page")[-1].find('a').text)
        films_index = {}

        # TODO async await
        for page_num in range(num_pages):
            url = self._build_user_watchlist_url(user_id)

            if (page_num != 0):
                url += f"/page/{page_num + 1}/"

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
        print(url)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36","X-Requested-With": "XMLHttpRequest"})
        return urllib.request.urlopen(req).read()
        # def fetch_source():
        #     req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36","X-Requested-With": "XMLHttpRequest"})
        #     return urllib.request.urlopen(req).read()

        # return self.ds.get( 'requests', url, fetch_source )
