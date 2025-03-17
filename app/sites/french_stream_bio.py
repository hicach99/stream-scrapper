from app.models import Episode, Movie, Link, Season, Serie
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.sites.scrapper import wait_until_title_contains
from urllib.parse import urlparse
from app.sites.tools import add_message_to_file, search_select_movie, search_select_serie
import traceback, sys, re, time

duration=50

validated_versions=['truefrench','subfrench','vostfr','french','fr','vf']
vf_versions=['truefrench','french', 'vf', 'fr']
vostfr_versions=['vostfr','subfrench']

page_item_box='a.short-poster.img-box.with-mask'
page_item_box_title='div.short-title'

finished = []

class tmd:
    def __init__(self, id):
        self.id = id

def get_host(page_link):
    parsed_url = urlparse(page_link)
    return parsed_url.netloc if parsed_url.netloc else parsed_url.path.split('/')[0]

def str_int(s):
    match = re.search(r'\d+', s)
    if match:
        return int(match.group())
    return None

def set_link_version(version):
    if version.lower() in vostfr_versions:return 'VOSTFR'
    elif version.lower() in vf_versions:return 'VF'
def validate_link(version : str,default=None):
    for v in validated_versions:
        if v in version.lower() or version.lower() in v:
            return set_link_version(v)
    return default
def get_year(driver,link):
    
    #driver.get(link)
    driver.uc_open_with_reconnect(link, 2)
    driver.uc_gui_click_captcha()

    wait = WebDriverWait(driver, duration)
    wait_until_title_contains(driver, wait)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    return html.select_one('#dle-content > article > div.fmain > div.fcols.fx-row > div.fmid > div.flist.clearfix > ul:nth-child(2) > li:nth-child(3) > span').get_text().strip()
# load a movie
def load_movie_links(driver : webdriver.Chrome,movie: Movie,loaded=False):
    if not loaded:
        
        #driver.get(movie.source_link)
        driver.uc_open_with_reconnect(movie.source_link, 2)
        driver.uc_gui_click_captcha()

        wait = WebDriverWait(driver, duration)
        wait_until_title_contains(driver, wait)
    html = BeautifulSoup(driver.page_source, 'html.parser')

    skin = html.select_one("#version-switcher-form > input[name='skin_name']")['value']
    if skin=='VFV1':
        submit_button = driver.find_element(By.CSS_SELECTOR, "#version-switcher-form > button")
        submit_button.click()
        wait = WebDriverWait(driver, duration)
        wait_until_title_contains(driver, wait)
        html = BeautifulSoup(driver.page_source, 'html.parser')

    movie_quality=html.select_one('#film_quality > a').get_text()
    movie_version=html.select_one('#film_lang > a').get_text()
    movie_links_items=html.select('div.version-option')
        
    movie_links_versions=[l['data-version'] for l in movie_links_items]
    movie_links_hrefs=[l['data-url'] for l in movie_links_items]
    movie.quality=movie_quality
    movie.save()
    
    mli = html.select('button.player-option')
    mlh = [l['data-url-default'] for l in mli]
    mlv = [movie_quality * len(mlh)]

    movie_links_hrefs.extend(mlh)
    movie_links_versions.extend(mlv)

    content_links,header_links=[],[]
    for i in range(len(movie_links_versions)):
        version = validate_link(movie_links_versions[i],None)
        if version:
            content_links.append(Link(embed_link=movie_links_hrefs[i],version=version,movie=movie))
        else:
            header_links.append(Link(embed_link=movie_links_hrefs[i],version=set_link_version(movie_version),movie=movie))
    if content_links:
        for link in content_links:
            try:
                Link.objects.get(embed_link=link.embed_link,movie=movie)
            except:
                link.save()
    else:
        for link in header_links:
            try:
                Link.objects.get(embed_link=link.embed_link,movie=movie)
            except:
                link.save()
def get_other_seasons_link(driver : webdriver.Chrome,link : str):
    driver.uc_open_with_reconnect(link, 2)
    driver.uc_gui_click_captcha()
    wait = WebDriverWait(driver, duration)
    wait_until_title_contains(driver, wait)
    
    html = BeautifulSoup(driver.page_source, 'html.parser')
    skin = html.select_one("#version-switcher-form > input[name='skin_name']")['value']
    if skin=='VFV1':
        submit_button = driver.find_element(By.CSS_SELECTOR, "#version-switcher-form > button")
        submit_button.click()
        wait = WebDriverWait(driver, duration)
        wait_until_title_contains(driver, wait)
        html = BeautifulSoup(driver.page_source, 'html.parser')
    host = get_host(link)
    try:
        o_seasons_link = "https://"+host+html.select_one(".collapsible-header > p > a")["href"]
    except:
        try:
            o_seasons_link = "https://"+host+html.select_one(".fmain > p > a")["href"]
        except:
            o_seasons_link = None
    return o_seasons_link 
# load a season
def load_season_links(driver : webdriver.Chrome,season: Season,loaded=False, other_seasons = False):
    if not loaded:
        
        #driver.get(season.source_link)
        driver.uc_open_with_reconnect(season.source_link, 2)
        driver.uc_gui_click_captcha()

        wait = WebDriverWait(driver, duration)
        wait_until_title_contains(driver, wait)
    
    html = BeautifulSoup(driver.page_source, 'html.parser')
    skin = html.select_one("#version-switcher-form > input[name='skin_name']")['value']
    if skin=='VFV1':
        submit_button = driver.find_element(By.CSS_SELECTOR, "#version-switcher-form > button")
        submit_button.click()
        wait = WebDriverWait(driver, duration)
        wait_until_title_contains(driver, wait)
        html = BeautifulSoup(driver.page_source, 'html.parser')

    if other_seasons:
        host = get_host(season.source_link)
        o_seasons_link = "https://"+host+html.select_one(".collapsible-header > p > a")["href"]
        return o_seasons_link if o_seasons_link else "https://"+host+html.select_one(".fmain > p > a")["href"]

    vf_a_tags=html.select_one('.VOSTFR-tab').find_next_sibling(class_='elink').select('a.fstab')
    vostfr_a_tags=html.select_one('.VF-tab').find_next_sibling(class_='elink').select('a.fstab')
    for a in vf_a_tags:
        ep = None
        try:
            ep = {'num':str_int(a['title']),'rel':a['data-rel']}
            try:
                episode=Episode.objects.get(episode_number=ep['num'],season=season)
            except:
                episode=Episode.objects.create(episode_number=ep['num'],season=season)
            try:
                links=[a['href'] for a in html.select_one('#'+ep['rel']).select('a.fsctab')]
                for link in links:
                    try:
                        Link.objects.get(embed_link=link,episode=episode)
                    except:
                        Link.objects.create(embed_link=link,version='VF',episode=episode)
            except:
                pass
        except:pass
    for a in vostfr_a_tags:
        ep = None
        try:
            ep = {'num':str_int(a['title']),'rel':a['data-rel']}
            try:
                episode=Episode.objects.get(episode_number=ep['num'],season=season)
            except:
                episode=Episode.objects.create(episode_number=ep['num'],season=season)
            try:
                links=[a['href'] for a in html.select_one('#'+ep['rel']).select('a.fsctab')]
                for link in links:
                    try:
                        Link.objects.get(embed_link=link,episode=episode)
                    except:
                        Link.objects.create(embed_link=link,version='VOSTFR',episode=episode)
            except:
                pass
        except:pass

# load a movies page
def load_movies_page(driver : webdriver.Chrome,page_link : str, page = None):
    
    #driver.get(page_link)
    driver.uc_open_with_reconnect(page_link, 2)
    driver.uc_gui_click_captcha()

    host = get_host(page_link)
    wait = WebDriverWait(driver, duration)
    wait_until_title_contains(driver, wait)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    movies_items=html.select(page_item_box)
    movies_names=html.select(page_item_box_title)
    movies_links=["https://"+host+item['href'] for item in movies_items]
    movies_names=[item.get_text().strip() for item in movies_names]
    for i, title in enumerate(movies_names):
        year=get_year(driver,movies_links[i])
        tmdb_movie=search_select_movie(title,year)
        if tmdb_movie:
            try:
                try:
                    movie=Movie.objects.get(id=tmdb_movie.id)
                except:
                    movie=Movie.objects.create(id=tmdb_movie.id,source_link=movies_links[i])
                load_movie_links(driver, movie,True)
                print(f'[+] the movie: {title} page {page} was loaded successfully')
            except Exception as e:
                add_message_to_file('failed_page_movies.txt',f'{page}: {title}: {movies_links[i]} - {e}: ' + str(traceback.extract_tb(sys.exc_info()[-1])) )
                print(f'[-] error loading the movie: {title} page {page} due to: {e}:',traceback.extract_tb(sys.exc_info()[-1]))
                if "invalid session id" in str(e).lower() or 'connection not available' in str(e).lower():
                    sys.exit()
        else:
            add_message_to_file('failed_page_movies.txt',f'{title}: {movies_links[i]} - no tmdb movie found')
            print(f'[-] error loading the movie: {title} due to: no tmdb movie found')
# load a series page
def get_number_boxes(driver, page_link):
    driver.uc_open_with_reconnect(page_link, 2)
    driver.uc_gui_click_captcha()
    wait = WebDriverWait(driver, duration)
    wait_until_title_contains(driver, wait)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    series_items=html.select(page_item_box)
    return len(series_items)
def load_series_page(driver : webdriver.Chrome,page_link : str, other_seasons = True, sid = None,page = None):
    global finished
    #driver.get(page_link)
    driver.uc_open_with_reconnect(page_link, 2)
    driver.uc_gui_click_captcha()

    host = get_host(page_link)
    wait = WebDriverWait(driver, duration)
    wait_until_title_contains(driver, wait)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    series_items=html.select(page_item_box)
    series_items_names=html.select(page_item_box_title)
    series_links=["https://"+host+item['href'] for item in series_items]
    series_names=[item.get_text().strip().split(' - ')[0] for item in series_items_names]
    series_seasons=[]
    for i,item in enumerate(series_items):
        try:
            series_seasons.append(int(series_links[i].split('saison-')[-1].split('-')[0].split('.')[0]))
        except:
            try:
                num=series_items_names[i].get_text().strip().split(' - ')[1].split(' ')[-1]
                series_seasons.append(int(num))
            except:
                series_seasons.append(1)
    for i, title in enumerate(series_names):
        # number of seasons
        other_seasons_link = None
        if not sid:
            other_seasons_link = get_other_seasons_link(driver,series_links[i])
            try:
                nb_seasons = get_number_boxes(driver, other_seasons_link+"/page/1")
            except:
                nb_seasons = series_seasons[i]
            tmdb_serie=search_select_serie(title,nb_seasons if other_seasons_link else series_seasons[i])
        else:
            tmdb_serie = tmd(sid)
        if tmdb_serie and (not tmdb_serie.id in finished):
            try:
                try:
                    serie=Serie.objects.get(id=tmdb_serie.id)
                except:
                    serie=Serie.objects.create(id=tmdb_serie.id)
                try:
                    season=Season.objects.get(serie=serie,season_number=series_seasons[i])
                except Exception as e:
                    raise Exception(f'[-] Number of season unclear for: {title} : {e}')
                season.source_link=series_links[i]
                season.save()
                if other_seasons_link and other_seasons:
                    load_series_page(driver, other_seasons_link+"/page/1", other_seasons = False, sid = serie.id, page=page)
                else:
                    load_season_links(driver,season)
                print(f'[+] the serie: {title} page {page} '+('' if other_seasons else f'season {series_seasons[i]} ')+'was loaded successfully')
                if other_seasons: finished.append(serie.id)
            except Exception as e:
                add_message_to_file('failed_page_seasons.txt',f'{page}: {title} season {series_seasons[i]}: {series_links[i]} - {e}: ' + str(traceback.extract_tb(sys.exc_info()[-1])) )
                print(f'[-] error loading the serie: {title} page {page} '+('' if other_seasons else f'season {series_seasons[i]} ')+ f'due to: {e}:', traceback.extract_tb(sys.exc_info()[-1]))
                if "invalid session id" in str(e).lower() or 'connection not available' in str(e).lower():
                    sys.exit()
        else:
            if (not tmdb_serie) or (not tmdb_serie.id in finished):
                add_message_to_file('failed_page_seasons.txt',f'{title} season {series_seasons[i]}: {series_links[i]} - no tmdb serie found')
                print(f'[-] error loading the serie: {title} season {series_seasons[i]}  due to: no tmdb serie found')
            else:
                print(f'[!] info loading the serie: {title} already added')

    if not other_seasons and len(series_names)>=18:
        parts = page_link.split('/')
        new_link = '/'.join(parts[0:-1]) +'/'+ str(int(parts[-1])+1)
        load_series_page(driver, new_link, other_seasons = False, sid = sid, page=page)
def load_movies_pages(driver : webdriver.Chrome, pages_link : str, start: int, end:int, asc:bool):
    pages_range = range(start, end+1) if asc else range(end, start-1, -1)
    for i in pages_range:
        page_link=(pages_link if pages_link[-1]=='/' else pages_link+'/') + str(i)
        try:
            load_movies_page(driver,page_link,page = i)
            print(f'[+] page {i} was loaded successfully')
            add_message_to_file('movies_pages.txt',f'[+] movies page {i}')
        except Exception as e:
            add_message_to_file('failed_movies_pages.txt',f'page {i}:{page_link} - {e}: ' + str(traceback.extract_tb(sys.exc_info()[-1])) )
            print(f'[-] error loading page {i} due to: {e}:', traceback.extract_tb(sys.exc_info()[-1]))
            if "invalid session id" in str(e).lower():
                sys.exit()
def load_series_pages(driver : webdriver.Chrome, pages_link : str, start: int, end:int, asc:bool=True):
    global finished
    pages_range = range(start, end+1) if asc else range(end, start-1, -1)
    finished = []
    for i in pages_range:
        page_link=str(pages_link if pages_link[-1]=='/' else pages_link+'/') + str(i)
        try:
            load_series_page(driver,page_link,page = i)
            print(f'[+] page {i} was loaded successfully')
            add_message_to_file('series_pages.txt',f'[+] series page {i}')
        except Exception as e:
            add_message_to_file('failed_series_pages.txt',f'page {i}:{page_link} - {e}: ' + str(traceback.extract_tb(sys.exc_info()[-1])) )
            print(f'[-] error loading page {i} due to: {e}:', traceback.extract_tb(sys.exc_info()[-1]))
            if "invalid session id" in str(e).lower():
                sys.exit()
