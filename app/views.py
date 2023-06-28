from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from app.sites import french_stream_bio, wiflix_surf
from app.sites.scrapper import init_driver
from app.models import Movie, Season, Serie

scrapper={
    'wiflix.surf':{
        'load_movie': wiflix_surf.load_movie_links,
        'load_season': wiflix_surf.load_season_links,
        'load_page': {
            'movie':wiflix_surf.load_movies_page,
            'season':wiflix_surf.load_series_page,
        },
        'load_pages': {
            'movie':wiflix_surf.load_movies_pages,
            'season':wiflix_surf.load_series_pages,
        },
    },
    'french-stream.gg':{
        'load_movie': french_stream_bio.load_movie_links,
        'load_season': french_stream_bio.load_season_links,
        'load_page': {
            'movie':french_stream_bio.load_movies_page,
            'season':french_stream_bio.load_series_page,
        },
        'load_pages': {
            'movie':french_stream_bio,
            'season':french_stream_bio,
        },
    }
}

def detect_website(link:str):
    parts=link.split('//')[1].split('/')[0].split('.')
    return parts[-2]+'.'+parts[-1]

def test(request):
    a=Serie.get_tmdb(46952)
    return HttpResponse([a], content_type='application/json')

def load_movie(request,id):
    movie=Movie.objects.get(id=id)
    driver=init_driver()
    website=detect_website(movie.source_link)
    try:
        scrapper[website]['load_movie'](driver,movie)
        messages.success(request, f'{movie} was loaded successful!')
    except Exception as e:
        messages.error(request, f'{movie} was not loaded due to: {e}')
    driver.quit()
    return redirect('admin:app_movie_change', object_id=id)

def load_season(request,id):
    season=Season.objects.get(id=id)
    driver=init_driver()
    website=detect_website(season.source_link)
    try:
        scrapper[website]['load_season'](driver,season)
        messages.success(request, f'{season} was loaded successful!')
    except Exception as e:
        messages.error(request, f'{season} was not loaded due to: {e}')
    driver.quit()
    return redirect('admin:app_season_change', object_id=id)

def load_page(request,model):
    try:
        if request.method=='POST':
            page_link=request.POST['page_link']
            driver=init_driver()
            website=detect_website(page_link)
            try:
                scrapper[website]['load_page'][model](driver,page_link)
            except Exception as e:
                raise e
            messages.success(request, f'{model}s page was loaded successful!')
        else:
            raise Exception("method was not POST method")
    except Exception as e:
        messages.error(request, f'{model}s page was not loaded due to: {e}')
    driver.quit()
    return redirect(f'admin:app_{model}_changelist')

def load_pages(request,model):
    try:
        if request.method=='POST':
            pages_link,start,end,asc=request.POST['pages_link'],int(request.POST['start']),int(request.POST['end']),True if request.POST['order'] == 'asc' else False
            driver=init_driver()
            website=detect_website(pages_link)
            try:
                scrapper[website]['load_pages'][model](driver,pages_link,start,end,asc)
            except Exception as e:
                raise e         
            messages.success(request, f'{model}s page was loaded successful!')
        else:
            raise Exception("method was not POST method")
    except Exception as e:
        messages.error(request, f'{model}s pages was not loaded due to: {e}')
    driver.quit()
    return redirect(f'admin:app_{model}_changelist')
