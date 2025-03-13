from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from app.sites import french_stream_bio, wiflix_surf
from app.sites.scrapper import init_driver
from app.models import Movie, PopularMovie, PopularSerie, Season, Serie, TopRatedMovie, TopRatedSerie, UpcomingMovie, UpcomingSerie
from app.sites.tools import get_exception_details

scrapper={
    'wiflix':{
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
    'french-stream':{
        'load_movie': french_stream_bio.load_movie_links,
        'load_season': french_stream_bio.load_season_links,
        'load_page': {
            'movie':french_stream_bio.load_movies_page,
            'season':french_stream_bio.load_series_page,
        },
        'load_pages': {
            'movie':french_stream_bio.load_movies_pages,
            'season':french_stream_bio.load_series_pages,
        },
    }
}
models={
    'movie':Movie,
    'serie':Serie,
}
banners_models={
    'popularmovie':Movie,
    'popularserie':Movie,
    'topratedmovie':Movie,
    'topratedserie':Movie,
    'upcomingmovie':Movie,
    'upcomingserie':Movie,
}

def detect_website(link:str):
    for web in scrapper:
        if web in link:
            return  web

def test(request):
    return redirect('/admin')
    a=Movie.get_tmdb(603692)
    return HttpResponse([a], content_type='application/json')

def load_movie(request,id):
    movie=Movie.objects.get(id=id)
    driver=init_driver()
    french_stream_bio.connect_vpn(driver)
    website=detect_website(movie.source_link)
    try:
        scrapper[website]['load_movie'](driver,movie)
        messages.success(request, f'{movie} was loaded successful!')
    except Exception as e:
        messages.error(request, f'{movie} was not loaded due to: {e} in {get_exception_details(e)}')
    driver.quit()
    return redirect('admin:app_movie_change', object_id=id)

def load_season(request,id):
    season=Season.objects.get(id=id)
    driver=init_driver()
    french_stream_bio.connect_vpn(driver)
    website=detect_website(season.source_link)
    try:
        scrapper[website]['load_season'](driver,season)
        messages.success(request, f'{season} was loaded successful!')
    except Exception as e:
        messages.error(request, f'{season} was not loaded due to: {e} in {get_exception_details(e)}')
    driver.quit()
    return redirect('admin:app_season_change', object_id=id)

def load_page(request,model):
    driver=None
    try:
        if request.method=='POST':
            page_link=request.POST['page_link']
            driver=init_driver()
            french_stream_bio.connect_vpn(driver)
            website=detect_website(page_link)
            try:
                scrapper[website]['load_page'][model](driver,page_link)
            except Exception as e:
                raise e
            messages.success(request, f'{model}s page was loaded successful!')
        else:
            raise Exception("method was not POST method")
    except Exception as e:
        messages.error(request, f'{model}s page was not loaded due to: {e} in {get_exception_details(e)}')
    if driver:driver.quit()
    return redirect(f'admin:app_{model}_changelist')

def load_pages(request,model):
    driver=None
    try:
        if request.method=='POST':
            pages_link,start,end,asc=request.POST['pages_link'],int(request.POST['start']),int(request.POST['end']),True if request.POST['order'] == 'asc' else False
            driver=init_driver()
            french_stream_bio.connect_vpn(driver)
            website=detect_website(pages_link)
            try:
                scrapper[website]['load_pages'][model](driver,pages_link,start,end,asc)
            except Exception as e:
                raise e         
            messages.success(request, f'{model}s page was loaded successful!')
        else:
            raise Exception("method was not POST method")
    except Exception as e:
        messages.error(request, f'{model}s pages was not loaded due to: {e} in {get_exception_details(e)}')
    if driver:driver.quit()
    return redirect(f'admin:app_{model}_changelist')

def update_data(request,model_name):
    try:
        model=models[model_name]
        for item in model.objects.all():
            try:
                item.generated=False
                item.save()
            except Exception as e:
                print('[-]',model_name, item.title,'is ignored')
        messages.success(request, f'{model_name}s where updated successfully!')
    except Exception as e:
        messages.error(request, f'{model_name}s where not updated successfully! due to: {e}')
    return redirect(f'admin:app_{model_name}_changelist')

def generate_data(request,model_name):
    try:
        model=banners_models[model_name]
        obj=('movie' if 'movie' in model_name else 'serie')
        if 'popular' in model_name:
            if 'movie' in model_name:
                PopularMovie.generate_data()
            else:
                PopularSerie.generate_data()
        elif 'upcoming' in model_name: 
            if 'movie' in model_name:
                UpcomingMovie.generate_data()
            else:
                UpcomingSerie.generate_data()
        else:
            if 'movie' in model_name:
                TopRatedMovie.generate_data()
            else:
                TopRatedSerie.generate_data()
        messages.success(request, f'{obj}s where generated successfully!')
    except Exception as e:
        messages.error(request, f'{obj}s where not generated successfully! due to: {e}')
    return redirect(f'admin:app_{model_name}_changelist')