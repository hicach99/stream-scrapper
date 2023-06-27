from app.models import Episode, Movie, Link, Season, Serie
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from app.sites.scrapper import wait_until_title_contains

from app.sites.tools import add_message_to_file, search_select_movie, search_select_serie

duration=50

validated_versions=['truefrench','subfrench','vostfr','french','fr','vf']
vf_versions=['truefrench','french', 'vf', 'fr']
vostfr_versions=['vostfr','subfrench']

page_item_box='a.short-poster.img-box.with-mask'
page_item_box_title='.short-title'

def set_link_version(version):
    if version.lower() in vostfr_versions:return 'VOSTFR'
    elif version.lower() in vf_versions:return 'VF'
def validate_link(version : str,default=None):
    for v in validated_versions:
        if v in version.lower() or version.lower() in v:
            return set_link_version(v)
    return default
def get_year(driver,link):
    driver.get(link)
    wait = WebDriverWait(driver, duration)
    wait_until_title_contains(driver, wait)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    return html.select_one('.flist.clearfix  .flist-col:nth-child(2) li:nth-child(3)').get_text().strip()
# load a movie
def load_movie_links(driver : webdriver.Chrome,movie: Movie,loaded=False):
    if not loaded:
        driver.get(movie.source_link)
        wait = WebDriverWait(driver, duration)
        wait_until_title_contains(driver, wait)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    movie_quality=html.select_one('#film_quality > a').get_text()
    movie_version=html.select_one('#film_lang > a').get_text()
    movie_links_items=html.select('#gGotop')
    movie_links_versions=[i.get_text() for i in movie_links_items]
    movie_links_hrefs=[l['href'] for l in movie_links_items]
    movie.quality=movie_quality
    movie.save()
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
# load a season
def load_season_links(driver : webdriver.Chrome,season: Season,loaded=False):
    if not loaded:
        driver.get(season.source_link)
        wait = WebDriverWait(driver, duration)
        wait_until_title_contains(driver, wait)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    vf_a_tags=html.select_one('.VOSTFR-tab').find_next_sibling(class_='elink').select('a.fstab')
    vostfr_a_tags=html.select_one('.VF-tab').find_next_sibling(class_='elink').select('a.fstab')
    vf_episodes_data=[{'num':int(a['title'][-1]),'rel':a['data-rel']} for a in vf_a_tags]
    vostfr_episodes_data=[{'num':int(a['title'][-1]),'rel':a['data-rel']} for a in vostfr_a_tags]
    for ep in vf_episodes_data:
        try:
            episode=Episode.objects.get(episode_number=ep['num'],season=season)
        except:
            episode=Episode.objects.create(episode_number=ep['num'],season=season)
        links=[a['href'] for a in html.select_one('#'+ep['rel']).select('a.fsctab')]
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
        links=[a['href'] for a in html.select_one('#'+ep['rel']).select('a.fsctab')]
        for link in links:
            try:
                Link.objects.get(embed_link=link,episode=episode)
            except:
                Link.objects.create(embed_link=link,version='VOSTFR',episode=episode)
# load a movies page
def load_movies_page(driver : webdriver.Chrome,page_link : str):
    driver.get(page_link)
    wait = WebDriverWait(driver, duration)
    wait_until_title_contains(driver, wait)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    movies_items=html.select(page_item_box)
    movies_links=[item['href'] for item in movies_items]
    movies_names=[item.select_one(page_item_box_title).get_text().strip() for item in movies_items]
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
                print(f'[+] the movie: {title} was loaded successfully')
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
    series_names=[item.select_one(page_item_box_title).get_text().strip().split(' - ')[0] for item in series_items]
    series_seasons=[]
    for i,item in enumerate(series_items):
        num=item.select_one(page_item_box_title).get_text().strip().split(' - ')[1].split(' ')[-1]
        try:
            series_seasons.append(int(num))
        except:
            try:
                series_seasons.append(int(series_links[i].split('-')[-1].split('.')[0]))
            except:
                series_seasons.append(num)
    print(series_seasons)
    for i, title in enumerate(series_names):
        tmdb_serie=search_select_serie(title,series_seasons[i])
        if tmdb_serie:
            try:
                try:
                    serie=Serie.objects.get(id=tmdb_serie.id)
                except:
                    serie=Serie.objects.create(id=tmdb_serie.id)
                try:
                    season=Season.objects.get(serie=serie,season_number=series_seasons[i])
                except:
                    raise Exception(f'No tmdb serie matches: {title}')
                season.source_link=series_links[i]
                season.save()
                load_season_links(driver,season)
                # other_seasons=load_season_links(driver,season)
                # for s in other_seasons:
                #     try:
                #         o_season=Season.objects.get(serie=serie,season_number=s['num'])
                #         o_season.source_link=s['link']
                #         o_season.save()
                #         load_season_links(driver,o_season)
                #         print(f'[+] the serie: {title} season {o_season.season_number} was loaded successfully')
                #     except:
                #         add_message_to_file('failed_page_seasons.txt',f'{title} season {o_season.season_number}: {o_season.source_link} - {e}')
                #         print(f'[-] error loading the serie: {title} season {o_season.season_number}  due to: {e}')
                print(f'[+] the serie: {title} season {series_seasons[i]} was loaded successfully')
            except Exception as e:
                add_message_to_file('failed_page_seasons.txt',f'{title} season {series_seasons[i]}: {series_links[i]} - {e}')
                print(f'[-] error loading the serie: {title} season {series_seasons[i]}  due to: {e}')
        else:
            add_message_to_file('failed_page_seasons.txt',f'{title} season {series_seasons[i]}: {series_links[i]} - no tmdb serie found')
            print(f'[-] error loading the serie: {title} season {series_seasons[i]}  due to: no tmdb serie found')
