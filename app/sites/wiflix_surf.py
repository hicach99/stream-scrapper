from app.models import Episode, Movie, Link, OtherTitle, Season, Serie
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from app.sites.scrapper import wait_until_title_contains
from app.sites.tools import add_message_to_file, search_select_movie, search_select_serie

duration=100

validated_versions=['truefrench','subfrench','vostfr','french','fr','vf']
vf_versions=['truefrench','french', 'vf', 'fr']
vostfr_versions=['vostfr','subfrench']

page_item_box='.mov.clearfix > a.mov-t.nowrap'
page_item_box_season='.mov.clearfix > .nbloc1-2 .block-sai'

def get_year(driver,link):
    driver.get(link)
    wait = WebDriverWait(driver, duration)
    wait_until_title_contains(driver, wait)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    year_element=html.select_one('div.mov-label:-soup-contains("Date de sortie:") + div.mov-desc')
    if year_element:
        return year_element.get_text().strip()
    return None
def set_link_version(version):
    if version.lower() in vostfr_versions:return 'VOSTFR'
    elif version.lower() in vf_versions:return 'VF'
def validate_link(version : str,default=None):
    for v in validated_versions:
        if v in version.lower() or version.lower() in v:
            return set_link_version(v)
    return default
# load a movie
def load_movie_links(driver : webdriver.Chrome,movie: Movie,loaded=False):
    if not loaded:
        driver.get(movie.source_link)
        wait = WebDriverWait(driver, duration)
        wait_until_title_contains(driver, wait)
        print('[+] driver loaded successfully')
    html = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        movie_version=validate_link(html.select_one('div.mov-label:-soup-contains("Version:") + div.mov-desc').get_text())
    except:
        movie_version=None
    try:
        movie_quality=html.select_one('div.mov-label:-soup-contains("Qualité:") + div.mov-desc').get_text()
    except:
        movie_quality=None
    movie.quality=movie_quality
    movie.save()
    movie_links_hrefs=['https://'+l['href'].split('https://')[-1] for l in html.select('.linkstab > a')]
    movie_links_hrefs_secondary=['https://'+l['href'].split('https://')[-1] for l in html.select('.linkstab > div > a')]
    for href in movie_links_hrefs:
        try:
            Link.objects.get(embed_link=href,version=movie_version,movie=movie)
        except:
            Link.objects.create(embed_link=href,version=movie_version,movie=movie)
    for href in movie_links_hrefs_secondary:
        try:
            Link.objects.get(embed_link=href,version='VOSTFR' if movie_version=='VF' else 'VF',movie=movie)
        except:
            Link.objects.create(embed_link=href,version='VOSTFR' if movie_version=='VF' else 'VF',movie=movie)
# load a season
def load_season_links(driver : webdriver.Chrome,season: Season,loaded=False):
    if not loaded:
        driver.get(season.source_link)
        wait = WebDriverWait(driver, duration)
        wait_until_title_contains(driver, wait)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    vf_a_tags=html.select_one('.blocfr .stitle').find_next_sibling(class_='eplist').select('li.clicbtn')
    vostfr_a_tags=html.select_one('.blocvostfr .stitle').find_next_sibling(class_='eplist').select('li.clicbtn')
    vf_episodes_data=[{'num':int(a.get_text().split(' ')[-1]),'rel':a['rel']} for a in vf_a_tags]
    vostfr_episodes_data=[{'num':int(a.get_text().split(' ')[-1]),'rel':a['rel']} for a in vostfr_a_tags]
    for ep in vf_episodes_data:
        try:
            episode=Episode.objects.get(episode_number=ep['num'],season=season)
        except:
            episode=Episode.objects.create(episode_number=ep['num'],season=season)
        links=['https://'+a['href'].split('https://')[-1] for a in html.select_one('.'+ep['rel']).select('a')]
        for link in links:
            try:
                Link.objects.get(embed_link=link,episode=episode)
            except:
                Link.objects.create(embed_link=link,version='VF',episode=episode)
    for ep in vostfr_episodes_data:
        try:
            episode=Episode.objects.get(episode_number=ep['num'],season=season)
        except:
            episode=Episode.objects.create(episode_number=ep['num'],season=season)
        links=['https://'+a['href'].split('https://')[-1] for a in html.select_one('.'+ep['rel']).select('a')]
        for link in links:
            try:
                Link.objects.get(embed_link=link,episode=episode)
            except:
                Link.objects.create(embed_link=link,version='VOSTFR',episode=episode)
    other_seasons_items=html.select('div.mov-label:-soup-contains("Synopsis:") + div.mov-desc a')
    other_seasons=[]
    for a in other_seasons_items:
        other_seasons.append(
            {
                'num':int(a.select_one('b').get_text().split(' - ')[-1].split(' ')[-1]),
                'link':a['href'],
            }
        ) 
    return other_seasons
# load a movies page
def load_movies_page(driver : webdriver.Chrome,page_link : str):
    driver.get(page_link)
    wait = WebDriverWait(driver, duration)
    wait_until_title_contains(driver, wait)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    movies_items=html.select(page_item_box)
    movies_links=[item['href'] for item in movies_items]
    movies_names=[item.get_text().strip() for item in movies_items]
    for i, title in enumerate(movies_names):
        year=get_year(driver,movies_links[i])
        mm=None
        # if year:
        #     mm=Movie.search_by_title(title,year)
        searched_movie=mm[0] if mm else None
        if not searched_movie:
            tmdb_movie=search_select_movie(title,year)
        if searched_movie or tmdb_movie:
            try:
                if not searched_movie:
                    try:
                        movie=Movie.objects.get(id=tmdb_movie.id)
                    except:
                        movie=Movie.objects.create(id=tmdb_movie.id,source_link=movies_links[i])
                    if movie.title.lower() != title.lower() and movie.original_title.lower() != title.lower():
                        try:
                            OtherTitle.objects.get(movie=movie,title=title)
                        except:
                            OtherTitle.objects.create(movie=movie,title=title)
                else:
                    movie=searched_movie
                load_movie_links(driver, movie,True)
                print(f'[+] the movie {i+1}: {title} was loaded successfully')
            except Exception as e:
                add_message_to_file('failed_page_movies.txt',f'{title}: {movies_links[i]} - {e}')
                print(f'[-] error loading the movie: {title} due to: {e}')
        else:
            add_message_to_file('failed_page_movies.txt',f'{title}: {movies_links[i]} - no tmdb movie found')
            print(f'[-] error loading the movie: {title} due to: no tmdb movie found')
# load a series page
def load_series_page(driver : webdriver.Chrome,page_link : str):
    driver.get(page_link)
    wait = WebDriverWait(driver, duration)
    wait_until_title_contains(driver, wait)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    series_items=html.select(page_item_box)
    series_links=[item['href'] for item in series_items]
    series_names=[item.get_text().strip() for item in series_items]
    series_seasons=[]
    for i, item in enumerate(html.select(page_item_box_season)):
        try:
            series_seasons.append(int(item.get_text().strip().split(' ')[1].split('\n\t')[0]))
        except:
            try:
                series_seasons.append(int(series_links[i].split('-')[-1].split('.')[0]))
            except:
                series_seasons.append(None)
    for i, title in enumerate(series_names):
        ss=None #Serie.search_by_title(title,series_seasons[i])
        searched_serie=ss[0] if ss else None
        if not searched_serie:
            tmdb_serie=search_select_serie(title,series_seasons[i])
        if searched_serie or tmdb_serie:
            try:
                if not searched_serie:
                    try:
                        serie=Serie.objects.get(id=tmdb_serie.id)
                    except:
                        serie=Serie.objects.create(id=tmdb_serie.id)
                    if serie.title.lower() != title.lower() and serie.original_title.lower() != title.lower():
                        try:
                            OtherTitle.objects.get(serie=serie,title=title)
                        except:
                            OtherTitle.objects.create(serie=serie,title=title)
                else:
                    serie=searched_serie
                try:
                    season=Season.objects.get(serie=serie,season_number=series_seasons[i])
                except:
                    raise Exception(f'No tmdb serie matches: {title}')
                season.source_link=series_links[i]
                season.save()
                other_seasons=load_season_links(driver,season)
                for s in other_seasons:
                    try:
                        o_season=Season.objects.get(serie=serie,season_number=s['num'])
                        o_season.source_link=s['link']
                        o_season.save()
                        load_season_links(driver,o_season)
                        print(f'[+] the serie {i+1}-s{o_season.season_number}: {title} season {o_season.season_number} was loaded successfully')
                    except Exception as e:
                        add_message_to_file('failed_page_seasons.txt',f'{title} season {o_season.season_number}: {o_season.source_link} - {e}')
                        print(f'[-] error loading the serie: {title} season {o_season.season_number}  due to: {e}')
                print(f'[+] the serie {i+1}: {title} season {series_seasons[i]} was loaded successfully')
            except Exception as e:
                add_message_to_file('failed_page_seasons.txt',f'{title} season {series_seasons[i]}: {series_links[i]} - {e}')
                print(f'[-] error loading the serie: {title} season {series_seasons[i]}  due to: {e}')
        else:
            add_message_to_file('failed_page_seasons.txt',f'{title} season {series_seasons[i]}: {series_links[i]} - no tmdb serie found')
            print(f'[-] error loading the serie: {title} season {series_seasons[i]}  due to: no tmdb serie found')
def load_movies_pages(driver : webdriver.Chrome, pages_link : str, start: int, end:int, asc:bool):
    pages_range = range(start, end+1) if asc else range(end, start-1, -1)
    for i in pages_range:
        page_link=(pages_link if pages_link[-1]=='/' else pages_link+'/') + str(i)
        try:
            load_movies_page(driver,page_link)
            print(f'[+] page {i} was loaded successfully')
        except Exception as e:
            add_message_to_file('failed_pages.txt',f'page {i}:{page_link} - {e}')
            print(f'[-] error loading page {i} due to: {e}')
def load_series_pages(driver : webdriver.Chrome, pages_link : str, start: int, end:int, asc:bool):
    pages_range = range(start, end+1) if asc else range(end, start-1, -1)
    for i in pages_range:
        page_link=str(pages_link if pages_link[-1]=='/' else pages_link+'/') + str(i)
        try:
            load_series_page(driver,page_link)
            print(f'[+] page {i} was loaded successfully')
        except Exception as e:
            add_message_to_file('failed_pages.txt',f'page {i}:{page_link} - {e}')
            print(f'[-] error loading page {i} due to: {e}')