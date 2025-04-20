from letterboxd_api_interface import LetterboxdAPIInterface
from film import Film
from user import User
import urllib.request
from bs4 import BeautifulSoup

HIGHEST_RATING_TO_USE = 8

class LetterboxdScraper(LetterboxdAPIInterface):
    _build_user_watchlist_url  = staticmethod( lambda user_id : f"https://letterboxd.com/{user_id}/watchlist" )
    _build_user_films_url      = staticmethod( lambda user_id : f"https://letterboxd.com/{user_id}/films/by/member-rating" )
    _build_film_ratings_url    = staticmethod( lambda film_id : f"https://letterboxd.com/{film_id}/ratings" )

    # TODO dry up the fetching pattern, pass in a get_page fn and a get_content fn and a klass

    def __init__(self, ds):
        super().__init__(ds)

    # TODO rating / # viewers
    def get_film_metadata(self):
        pass

    # TODO 
    def get_list(self, list_id, bypass_cache=False):
        if not bypass_cache:
            list = self.ds.get('lists', list_id)
            if list:
                return list

    # TODO implement this VVV
    def _fetch(self, url, id, klass, fn_get_num_pages, fn_get_content, bypass_cache=False):
        if not bypass_cache:
            obj_data = self.ds.get(klass.datatype, id)
            if obj_data:
                return klass(id, obj_data)

        data = {}
        page = self._fetch_url(url)
        soup = BeautifulSoup(page, 'html.parser')

        num_pages = fn_get_num_pages(soup)
        print(num_pages)

        for page_num in range(num_pages):
            if (page_num != 0):
                page_url = url + f"/page/{page_num + 1}/"
                page = self._fetch_url(page_url)
            
            soup = BeautifulSoup(page, 'html.parser')

            # TODO can we pass here instead of writing to data?
            if not fn_get_content(soup, data):
                # is fetching complete
                break

        data_obj = klass( id, data )
        data_obj.save(self.ds)

        return data_obj

    def get_films_for_user(self, user_id, highest_rating_to_use=(HIGHEST_RATING_TO_USE+1), bypass_cache=False):

        def get_num_pages(soup):
            paginator = soup.find_all('li', class_="paginate-page")
            if paginator:
                return int(paginator[-1].find('a').text)
            else:
                return 1

        def get_content(soup, data):
            nonlocal highest_rating_to_use

            if 'watched_films' not in data:
                data['watched_films'] = {}

            film_lis = soup.find_all('li', class_="poster-container")            
            for film_li in film_lis:
                film_id = film_li.find('div', class_="film-poster").get('data-film-slug')

                rating_span = film_li.find('span', class_="rating")
                if rating_span:
                    rating = int(rating_span.get('class')[-1].split('-')[-1])
                else:
                    rating = None

                # TODO how to pass this in?
                # if rating and (page_num >= (num_pages / 3)) and rating == 10:
                #     # This user gives too many 10s. Ignore
                #     print('-> Too many 10s : skipping ', user_id)
                #     rating_index = {}
                #     encountered_all_ratings = True                    
                #     break

                if ( highest_rating_to_use != None ) and ( ( rating is None ) or ( rating < highest_rating_to_use ) ):
                    return False

                id = f"{user_id}:{film_id}"
                new_watch = {
                    'id'      : id,
                    'film_id' : film_id,
                    'user_id' : user_id,
                    'rating'  : rating,
                }

                data['watched_films'][film_id] = new_watch

            return True

        return self._fetch(
            self._build_user_films_url(user_id),
            user_id,
            User,
            get_num_pages,
            get_content,
            bypass_cache
        )

    # def get_films_for_user(self, user_id, highest_rating_to_use=(HIGHEST_RATING_TO_USE+1), bypass_cache=False):
    #     if not bypass_cache:
    #         user = self.ds.get('users', user_id)
    #         if user:
    #             return User(user)

    #     rating_index = {}
    #     encountered_all_ratings = False    

    #     page = self._fetch_url(self._build_user_films_url(user_id))
    #     soup = BeautifulSoup(page, 'html.parser')

    #     paginator = soup.find_all('li', class_="paginate-page")
    #     if paginator:
    #         num_pages = int(paginator[-1].find('a').text)
    #     else:
    #         num_pages = 1

    #     # TODO async await
    #     for page_num in range(num_pages):
    #         url = self._build_user_films_url(user_id)

    #         if (page_num != 0):
    #             url += f"/page/{page_num + 1}/"
    #             page = self._fetch_url(url)

    #         soup = BeautifulSoup(page, 'html.parser')

    #         film_lis = soup.find_all('li', class_="poster-container")
    #         for film_li in film_lis:
    #             film_id = film_li.find('div', class_="film-poster").get('data-film-slug')

    #             rating_span = film_li.find('span', class_="rating")
    #             if rating_span:
    #                 rating = int(rating_span.get('class')[-1].split('-')[-1])
    #             else:
    #                 rating = None

    #             if rating and (page_num >= (num_pages / 3)) and rating == 10:
    #                 # This user gives too many 10s. Ignore
    #                 print('-> Too many 10s : skipping ', user_id)
    #                 rating_index = {}
    #                 encountered_all_ratings = True                    
    #                 break

    #             if ( highest_rating_to_use != None ) and ( ( rating is None ) or ( rating < highest_rating_to_use ) ):
    #                 encountered_all_ratings = True
    #                 break

    #             id = f"{user_id}:{film_id}"
    #             new_watch = {
    #                 'id'      : id,
    #                 'film_id' : film_id,
    #                 'user_id' : user_id,
    #                 'rating'  : rating,
    #             }

    #             rating_index[film_id] = new_watch

    #         if encountered_all_ratings:
    #             break

    #     new_user = User( { 'id' : user_id, 'watched_films' : rating_index } )
    #     new_user.save(self.ds)

    #     return rating_index

    def get_ratings_for_film(self, film_id, highest_rating_to_use=(HIGHEST_RATING_TO_USE+1), bypass_cache=False):

        # TODO pagination
        def get_num_pages(soup):
            return 1

        def get_content(soup, data):
            nonlocal highest_rating_to_use

            if 'highest_rating_to_use' not in data:
                data['highest_rating_to_use'] = highest_rating_to_use

            if 'user_watches' not in data:
                data['user_watches'] = {}

            rating_groups = soup.find_all('section', class_="film-rating-group")
            for rating_group in rating_groups:
                rating_span = rating_group.find('span', class_="rating")
                if rating_span:
                    rating = int(rating_span.get('class')[-1].split('-')[-1])
                else:
                    rating = None

                if ( highest_rating_to_use != None ) and ( ( rating is None ) or ( rating < highest_rating_to_use ) ):
                    return False

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

                    data['user_watches'][user_id] = new_watch

            return True

        return self._fetch(
            self._build_film_ratings_url(film_id),
            film_id,
            Film,
            get_num_pages,
            get_content,
            bypass_cache
        )
    
    # def get_ratings_for_film(self, film_id, highest_rating_to_use=(HIGHEST_RATING_TO_USE+1), bypass_cache=False):
    #     if not bypass_cache:
    #         film = self.ds.get('films', film_id)

    #         if film:
    #             return Film(film)

    #     # TODO pagination
    #     encountered_all_ratings = False        
    #     rating_index = {}
    #     page = self._fetch_url(self._build_film_ratings_url(film_id))
    #     soup = BeautifulSoup(page, 'html.parser')

    #     rating_groups = soup.find_all('section', class_="film-rating-group")
    #     for rating_group in rating_groups:
    #         rating_span = rating_group.find('span', class_="rating")
    #         if rating_span:
    #             rating = int(rating_span.get('class')[-1].split('-')[-1])
    #         else:
    #             rating = None

    #         if ( highest_rating_to_use != None ) and ( ( rating is None ) or ( rating < highest_rating_to_use ) ):
    #             encountered_all_ratings = True
    #             break

    #         users = rating_group.find_all('a', class_="avatar")
    #         for user in users:
    #             user_id = user.get('href')[1:-1]
    #             id = f"{user_id}:{film_id}"
    #             new_watch = {
    #                 'id'      : id,
    #                 'film_id' : film_id,
    #                 'user_id' : user_id,
    #                 'rating'  : rating,
    #             }

    #             rating_index[user_id] = new_watch

    #         if encountered_all_ratings:
    #             break

    #     new_film = Film( { 'id' : film_id, 'user_watches' : rating_index } )
    #     new_film.save(self.ds)

    #     #TODO save film to DS
    #     return rating_index

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
