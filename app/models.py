import random, requests
from django.db import models
from tmdbv3api import TMDb, Movie as Tmdb_Movie,TV as Tmdb_Serie
from app.initial_data import load_initial_data

def get_tv_show_keywords(tv_id):
    url = f"https://api.themoviedb.org/3/tv/{tv_id}/keywords"
    params = {"api_key": random.choice(api_keys)}
    
    response = requests.get(url, params=params)
    response_json = response.json()
    
    result = {
        "id": response_json["id"],
        "results": []
    }
    
    for keyword in response_json["results"]:
        result["results"].append({
            "name": keyword["name"],
            "id": keyword["id"]
        })
    
    return result
class TmdbApi(models.Model):
    key = models.CharField(max_length=255,unique=True,default='')
    original_images_url='https://image.tmdb.org/t/p/original'
    def __str__(self):
        return self.key
tmdb = TMDb()
tmdb.language = 'fr'
movie_getter = Tmdb_Movie()
serie_getter = Tmdb_Serie()
allow_restoring_TmdbApi=True

try:
    if allow_restoring_TmdbApi:load_initial_data(TmdbApi)
    api_keys=[api.key for api in TmdbApi.objects.all()]
except:
    api_keys=None
class Video(models.Model):
    key = models.CharField(max_length=255,primary_key=True)
    name = models.CharField(max_length=255,blank=True,null=True)
    site = models.CharField(max_length=255,blank=True,null=True)
    movie = models.ForeignKey('Movie', related_name='videos', blank=True, on_delete=models.CASCADE,null=True)
    serie = models.ForeignKey('Serie', related_name='videos', blank=True, on_delete=models.CASCADE,null=True)
    @classmethod
    def save_if_not_exists(cls, videos_array,movie=None,serie=None):
        for v in videos_array[:10]:
            try:
                video=cls.objects.get(key=v.key)
            except:
                if movie:
                    video=cls.objects.create(key=v.key, name=v.name, site=v.site, movie=movie)
                elif serie:
                    video=cls.objects.create(key=v.key, name=v.name, site=v.site, serie=serie)
            video.save()
    def __str__(self):
        return self.site+': '+self.name

class Person(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255,blank=True,null=True)
    gender = models.IntegerField(default=1,null=True)
    popularity = models.FloatField(default=1,null=True)
    profile_path = models.CharField(max_length=255,blank=True,null=True)
    def __str__(self):
        return self.name

class Cast(models.Model):
    character = models.CharField(max_length=255,blank=True,null=True)
    person = models.ForeignKey(Person,on_delete=models.CASCADE,related_name='roles')
    movies = models.ManyToManyField('Movie', related_name='casts', blank=True)
    series = models.ManyToManyField('Serie', related_name='casts', blank=True)
    @classmethod
    def save_if_not_exists(cls, casts_array,movie=None,serie=None):
        for c in casts_array[:10]:
            try:
                cast=cls.objects.get(character=c.character,person__id=c.id)
            except:
                try:
                    person=Person.objects.get(id=c.id)
                except:
                    person=Person.objects.create(id=c.id,name=c.name,popularity=c.popularity,profile_path=c.profile_path)
                    try:
                        person.gender=c.gender
                    except:
                        pass
                    person.save()
                cast=cls.objects.create(person=person, character=c.character)
            cast.save()
            if movie and movie not in cast.movies.all():
                cast.movies.add(movie)
            elif serie and serie not in cast.series.all():
                cast.series.add(serie)
    def __str__(self):
        return self.person.name+' As '+self.character
    
class Director(models.Model):
    person = models.ForeignKey(Person,on_delete=models.CASCADE)
    movies = models.ManyToManyField('Movie', related_name='directors', blank=True)
    series = models.ManyToManyField('Serie', related_name='directors', blank=True)
    @classmethod
    def save_if_not_exists(cls, crew_array,movie=None,serie=None):
        for d in crew_array:
            if  movie and d.job=='Director':
                try:
                    director=cls.objects.get(person__id=d.id)
                except:
                    try:
                        person=Person.objects.get(id=d.id)
                    except:
                        person=Person.objects.create(id=d.id,name=d.name,profile_path=d.profile_path)
                        try:
                            person.gender=d.gender
                        except:
                            pass
                        person.save()
                    director=cls.objects.create(person=person)
                director.save()
                if movie not in director.movies.all():
                    director.movies.add(movie)
            elif serie:
                try:
                    director=cls.objects.get(person__id=d.id)
                except:
                    try:
                        person=Person.objects.get(id=d.id)
                    except:
                        person=Person.objects.create(id=d.id,name=d.name,profile_path=d.profile_path)
                        try:
                            person.gender=d.gender
                        except:
                            pass
                        person.save()
                    director=cls.objects.create(person=person)
                director.save()
                if serie not in director.series.all():
                    director.series.add(serie)
    def __str__(self):
        return self.person.name

class Movie(models.Model):
    id = models.IntegerField(primary_key=True)
    dmca = models.CharField(max_length=6,null=True,default='000000')
    source_link = models.CharField(max_length=512,blank=True,null=True)
    generated = models.BooleanField(default=False)
    adult = models.BooleanField(default=False)
    title = models.CharField(max_length=255,blank=True,null=True)
    original_title = models.CharField(max_length=255,blank=True,null=True)
    runtime = models.IntegerField(default=0,blank=True,null=True)
    overview = models.TextField(blank=True,null=True)
    countries = models.CharField(max_length=255,blank=True,null=True)
    release_date = models.DateField(blank=True,null=True)
    poster_path = models.CharField(max_length=255,blank=True,null=True)
    backdrop_path = models.CharField(max_length=255,blank=True,null=True)
    original_language = models.CharField(max_length=10,blank=True,null=True)
    popularity = models.FloatField(blank=True,null=True)
    vote_count = models.PositiveIntegerField(blank=True,null=True)
    vote_average = models.FloatField(blank=True,null=True)
    budget = models.FloatField(default=0,blank=True,null=True)
    revenue = models.FloatField(default=0,blank=True,null=True)
    quality = models.CharField(max_length=255,blank=True,null=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    def set_movie_details(self,movie):
        try:
            self.adult = movie.adult
            self.title = movie.title
            self.runtime = movie.runtime
            self.original_title = movie.original_title
            self.overview = movie.overview
            self.countries = ', '.join([i['iso_3166_1'] for i in movie.production_countries])
            if len(movie.release_date)>3: self.release_date = movie.release_date
            self.poster_path = movie.poster_path
            self.backdrop_path = movie.backdrop_path
            self.original_language = movie.original_language
            self.popularity = movie.popularity
            self.vote_count = movie.vote_count
            self.vote_average = movie.vote_average
            self.budget = movie.budget
            self.revenue = movie.revenue
        except Exception as e:
            pass
    def save(self, *args, **kwargs):
        if not self.generated:
            tmdb.api_key = random.choice(api_keys)
            movie = movie_getter.details(self.id)
            self.set_movie_details(movie)
            self.generated=True
            super().save(*args, **kwargs)
            curr_movie=Movie.objects.get(id=self.id)
            Genre.save_if_not_exists(movie.genres,movie=curr_movie)
            Keyword.save_if_not_exists(movie.keywords.keywords,movie=curr_movie)
            Cast.save_if_not_exists(movie.casts.cast,movie=curr_movie)
            Director.save_if_not_exists(movie.casts.crew,movie=curr_movie)
            Video.save_if_not_exists(movie.videos.results,movie=curr_movie)
        else:
            super().save(*args, **kwargs)
    def __str__(self):
        return self.title
    def version(self):
        vf=False
        vostfr=False
        for l in self.links.all():
            v=l.version
            if v == 'VF':vf=True
            elif v == 'VOSTFR':vostfr=True
            if vf and vostfr: return 'VF+VOSTFR'
        if vf: return 'VF'
        if vostfr: return 'VOSTFR'
        return '-'
    @classmethod
    def search_tmdb(cls,query:str):
        tmdb.api_key = random.choice(api_keys)
        return movie_getter.search(query)
    @classmethod
    def get_tmdb(cls,id:int):
        tmdb.api_key = random.choice(api_keys)
        return movie_getter.details(id)
    @classmethod
    def search_by_title(cls, query, year=None):
        queryset = cls.objects.filter(
            models.Q(other_titles__title__icontains=query) |
            models.Q(title__icontains=query) |
            models.Q(original_title__icontains=query)
        ).distinct()
        if year and year.isdigit():
            year = int(year)
            queryset = queryset.filter(release_date__year=year)
        return queryset
class Serie(models.Model):
    id = models.IntegerField(primary_key=True)
    dmca = models.CharField(max_length=6,null=True,default='000000')
    source_link = models.CharField(max_length=512,blank=True,null=True)
    generated = models.BooleanField(default=False)
    adult = models.BooleanField(default=False)
    in_production = models.BooleanField(default=False)
    title = models.CharField(max_length=255,blank=True,null=True)
    original_title = models.CharField(max_length=255,blank=True,null=True)
    runtime = models.IntegerField(default=0,blank=True,null=True)
    overview = models.TextField(blank=True,null=True)
    countries = models.CharField(max_length=255,blank=True,null=True)
    release_date = models.DateField(blank=True,null=True)
    poster_path = models.CharField(max_length=255,blank=True,null=True)
    backdrop_path = models.CharField(max_length=255,blank=True,null=True)
    original_language = models.CharField(max_length=10,blank=True,null=True)
    popularity = models.FloatField(blank=True,null=True)
    vote_count = models.PositiveIntegerField(blank=True,null=True)
    vote_average = models.FloatField(blank=True,null=True)
    number_of_seasons = models.IntegerField(default=0,blank=True,null=True)
    number_of_episodes = models.IntegerField(default=0,blank=True,null=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    def set_serie_details(self,serie):
        try:
            self.adult = serie.adult
            self.in_production = serie.in_production
            self.title = serie.name
            self.runtime = serie.episode_run_time[0] if serie.episode_run_time else None
            self.original_title = serie.original_name
            self.overview = serie.overview
            self.countries = ', '.join(serie.origin_country)
            if len(serie.first_air_date)>3: self.release_date = serie.first_air_date
            self.poster_path = serie.poster_path
            self.backdrop_path = serie.backdrop_path
            self.original_language = serie.original_language
            self.popularity = serie.popularity
            self.vote_count = serie.vote_count
            self.vote_average = serie.vote_average
            self.number_of_seasons = serie.number_of_seasons
            self.number_of_episodes = serie.number_of_episodes
        except Exception as e:
            pass
    def save(self, *args, **kwargs):
        if not self.generated:
            tmdb.api_key = random.choice(api_keys)
            serie = serie_getter.details(self.id)
            self.set_serie_details(serie)
            self.generated=True
            super().save(*args, **kwargs)
            curr_serie=Serie.objects.get(id=self.id)
            Genre.save_if_not_exists(serie.genres,serie=curr_serie)
            Keyword.save_if_not_exists(get_tv_show_keywords(self.id)['results'],serie=curr_serie)
            Season.save_if_not_exists(curr_serie,serie.seasons)
            Cast.save_if_not_exists(serie.credits.cast,serie=curr_serie)
            Director.save_if_not_exists(serie.created_by,serie=curr_serie)
            Video.save_if_not_exists(serie.videos.results,serie=curr_serie)
        else:
            super().save(*args, **kwargs)
    def __str__(self):
        return self.title
    @classmethod
    def search_tmdb(cls,query:str):
        tmdb.api_key = random.choice(api_keys)
        return serie_getter.search(query)
    @classmethod
    def get_tmdb(cls,id:int):
        tmdb.api_key = random.choice(api_keys)
        return serie_getter.details(id)
    def version(self):
        vf=False
        vostfr=False
        for l in self.seasons.all():
            v=l.version()
            if v == 'VF+VOSTFR' or v == 'VOSTFR+VF': return 'VF+VOSTFR'
            elif v == 'VF':vf=True
            elif v == 'VOSTFR':vostfr=True
            if vf and vostfr: return 'VF+VOSTFR'
        if vf: return 'VF'
        if vostfr: return 'VOSTFR'
        return '-'
    @classmethod
    def search_by_title(cls, query, season_number : int=None):
        queryset = cls.objects.filter(
            models.Q(other_titles__title__icontains=query) |
            models.Q(title__icontains=query) |
            models.Q(original_title__icontains=query)
        ).distinct()
        if season_number:
            queryset = queryset.filter(number_of_seasons__gte=season_number)
        return queryset
class Season(models.Model):
    id = models.IntegerField(primary_key=True)
    source_link = models.CharField(max_length=512,blank=True,null=True)
    release_date = models.DateField(blank=True,null=True)
    name = models.CharField(max_length=255,blank=True,null=True)
    overview = models.TextField(blank=True,null=True)
    poster_path = models.CharField(max_length=255,blank=True,null=True)
    season_number = models.IntegerField(default=0,blank=True,null=True)
    episode_count = models.IntegerField(default=0,blank=True,null=True)
    serie = models.ForeignKey('Serie', related_name='seasons', blank=True, on_delete=models.CASCADE,null=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    def __str__(self):
        return self.serie.title+' '+self.name
    def version(self):
        vf=False
        vostfr=False
        for l in self.episodes.all():
            v=l.version()
            if v == 'VF+VOSTFR' or v == 'VOSTFR+VF': return 'VF+VOSTFR'
            elif v == 'VF':vf=True
            elif v == 'VOSTFR':vostfr=True
            if vf and vostfr: return 'VF+VOSTFR'
        if vf: return 'VF'
        if vostfr: return 'VOSTFR'
        return '-'
    @classmethod
    def save_if_not_exists(cls, serie, seasons_array):
        for s in seasons_array:
            try:
                season=cls.objects.get(id=s.id)
            except:
                season=cls.objects.create(id=s.id,release_date=s.air_date, name=s.name, overview=s.overview, poster_path=s.poster_path, season_number=s.season_number, episode_count=s.episode_count, serie=serie)
            season.save()
class Episode(models.Model):
    episode_number = models.IntegerField(default=0,blank=True,null=True)
    season = models.ForeignKey('Season', related_name='episodes', blank=True, on_delete=models.CASCADE,null=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    def version(self):
        vf=False
        vostfr=False
        for l in self.links.all():
            v=l.version
            if v == 'VF':vf=True
            elif v == 'VOSTFR':vostfr=True
            if vf and vostfr: return 'VF+VOSTFR'
        if vf: return 'VF'
        if vostfr: return 'VOSTFR'
        return '-'
    def __str__(self):
        return str(self.season)+' Épisode '+str(self.episode_number)
class Link(models.Model):
    versions_choices=[
        ('VF','VF'),
        ('VOSTFR','VOSTFR'),
    ]
    embed_link = models.CharField(max_length=512,blank=True,null=True)
    version = models.CharField(max_length=255,blank=True,choices=versions_choices,null=True)
    movie = models.ForeignKey('Movie', related_name='links', blank=True, on_delete=models.CASCADE,null=True)
    episode = models.ForeignKey('Episode', related_name='links', blank=True, on_delete=models.CASCADE,null=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    def __str__(self):
        if self.movie:
            return 'lien '+str(self.id)+': '+str(self.movie)
        else:
            return 'lien '+str(self.id)+': '+str(self.episode)
class Genre(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    movies = models.ManyToManyField('Movie', related_name='genres', blank=True)
    series = models.ManyToManyField('Serie', related_name='genres', blank=True)
    def __str__(self):
        return self.name
    @classmethod
    def save_if_not_exists(cls, genres_array, movie=None,serie=None):
        for genre_data in genres_array:
            genre_id = genre_data['id']
            genre_name = genre_data['name']
            try:
                genre = cls.objects.get(id=genre_id)
            except:
                genre = cls.objects.create(id=genre_id,name=genre_name)
                genre.save()
            if movie and movie not in genre.movies.all():
                genre.movies.add(movie)
            elif serie and serie not in genre.series.all():
                genre.series.add(serie)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
class OtherTitle(models.Model):
    title = models.CharField(max_length=255,blank=True,null=True)
    movie = models.ForeignKey('Movie', related_name='other_titles', on_delete=models.CASCADE, null=True, blank=True)
    serie = models.ForeignKey(Serie, related_name='other_titles', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.title
class Visit(models.Model):
    movie = models.ForeignKey('Movie', related_name='visits', on_delete=models.CASCADE, null=True, blank=True)
    serie = models.ForeignKey('Serie', related_name='visits', on_delete=models.CASCADE, null=True, blank=True)
    season = models.ForeignKey('Season', related_name='visits', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('User', related_name='visits', on_delete=models.CASCADE, null=True, blank=True)
    platform = models.ForeignKey('Platform', related_name='visits', on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
class Like(models.Model):
    positive = models.BooleanField(default=True)
    movie = models.ForeignKey('Movie', related_name='likes', on_delete=models.CASCADE, null=True, blank=True)
    serie = models.ForeignKey('Serie', related_name='likes', on_delete=models.CASCADE, null=True, blank=True)
    season = models.ForeignKey('Season', related_name='likes', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey('Comment', related_name='likes', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('User', related_name='likes', on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
class Comment(models.Model):
    content = models.TextField(null=True, blank=True)
    movie = models.ForeignKey('Movie', related_name='comments', on_delete=models.CASCADE, null=True, blank=True)
    serie = models.ForeignKey('Serie', related_name='comments', on_delete=models.CASCADE, null=True, blank=True)
    season = models.ForeignKey('Season', related_name='comments', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('User', related_name='comments', on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
class Keyword(models.Model):
    name = models.CharField(max_length=255,blank=True,null=True)
    movie = models.ForeignKey('Movie', related_name='keywords', on_delete=models.CASCADE, null=True, blank=True)
    serie = models.ForeignKey(Serie, related_name='keywords', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.name
    @classmethod
    def save_if_not_exists(cls, keywords_array, movie=None,serie=None):
        for keyword_data in keywords_array:
            keyword_name = keyword_data['name']
            if movie:
                try:
                    cls.objects.get(name=keyword_name,movie=movie)
                except:
                    cls.objects.create(name=keyword_name,movie=movie)
            else:
                try:
                    cls.objects.get(name=keyword_name,serie=serie)
                except:
                    cls.objects.create(name=keyword_name,serie=serie)
class PopularMovie(models.Model):
    enabled = models.BooleanField(default=True)
    source = models.ForeignKey('Movie', related_name='popular_movies', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return str(self.source)
    @classmethod
    def generate_data(cls):
        tmdb.api_key = random.choice(api_keys)
        items_ids = [item.id for item in movie_getter.popular()]
        cls.objects.all().delete()
        for id in items_ids:
            try:
                item=Movie.objects.get(id=id)
                cls.objects.create(source=item)
            except:
                pass
class UpcomingMovie(models.Model):
    enabled = models.BooleanField(default=True)
    source = models.ForeignKey('Movie', related_name='upconing_movies', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return str(self.source)
    @classmethod
    def generate_data(cls):
        tmdb.api_key = random.choice(api_keys)
        items_ids = [item.id for item in movie_getter.upcoming()]
        cls.objects.all().delete()
        for id in items_ids:
            try:
                item=Movie.objects.get(id=id)
                cls.objects.create(source=item)
            except:
                pass
class TopRatedMovie(models.Model):
    enabled = models.BooleanField(default=True)
    source = models.ForeignKey('Movie', related_name='top_rated_movies', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return str(self.source)
    @classmethod
    def generate_data(cls):
        tmdb.api_key = random.choice(api_keys)
        items_ids = [item.id for item in movie_getter.top_rated()]
        cls.objects.all().delete()
        for id in items_ids:
            try:
                item=Movie.objects.get(id=id)
                cls.objects.create(source=item)
            except:
                pass
class PopularSerie(models.Model):
    enabled = models.BooleanField(default=True)
    source = models.ForeignKey('Serie', related_name='popular_series', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return str(self.source)
    @classmethod
    def generate_data(cls):
        tmdb.api_key = random.choice(api_keys)
        items_ids = [item.id for item in serie_getter.popular()]
        cls.objects.all().delete()
        for id in items_ids:
            try:
                item=Serie.objects.get(id=id)
                cls.objects.create(source=item)
            except:
                pass
class UpcomingSerie(models.Model):
    enabled = models.BooleanField(default=True)
    source = models.ForeignKey('Serie', related_name='upconing_series', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return str(self.source)
    @classmethod
    def generate_data(cls):
        tmdb.api_key = random.choice(api_keys)
        items_ids = [item.id for item in serie_getter.on_the_air()]
        cls.objects.all().delete()
        for id in items_ids:
            try:
                item=Serie.objects.get(id=id)
                cls.objects.create(source=item)
            except:
                pass
class TopRatedSerie(models.Model):
        enabled = models.BooleanField(default=True)
        source = models.ForeignKey('Serie', related_name='top_rated_series', on_delete=models.CASCADE, null=True, blank=True)
        def __str__(self):
            return str(self.source)
        @classmethod
        def generate_data(cls):
            tmdb.api_key = random.choice(api_keys)
            items_ids = [item.id for item in serie_getter.top_rated()]
            cls.objects.all().delete()
            for id in items_ids:
                try:
                    item=Serie.objects.get(id=id)
                    cls.objects.create(source=item)
                except:
                    pass
class User(models.Model):
    TYPE_CHOICES = (
        (0, 'Visitor'),
        (1, 'Movies Admin'),
        (2, 'Series Admin'),
        (3, 'Admin'),
        (4, 'Super Admin'),
    )
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    type = models.IntegerField(choices=TYPE_CHOICES, default=0)
    password = models.CharField(max_length=255)
    xp = models.FloatField(default=0.0)
    prize = models.FloatField(default=0.0)
    created_on = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True,auto_now_add=True,blank=True)
    platform = models.ForeignKey('Platform', related_name='users', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.username+' '+self.platform.domain_name
class Platform(models.Model):
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default='papystreaming'
    )
    domain_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default='papystreaming.vip'
    )
    url = models.CharField(
        max_length=255,
        blank=True,
        null=True,default='https://wvw.papystreaming.vip/'
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default="papystreaming film streaming et série streaming gratuit"
    )
    keywords=models.TextField(
        blank=True,
        null=True,
        default="film streaming, streaming, film, série streaming, papystreaming, du streaming, streamcomplet, stream complet"
    )
    meta_description=models.TextField(
        blank=True,
        null=True,
        default='papystreaming site du films et séries français, Film streaming et série streaming gratuit en vf 2021, Série streaming complet HD fr.'
    )
    description=models.TextField(
        blank=True,
        null=True,
        default='papystreaming Venez découvrir un site de streaming Papystreaming qui vous propose tout les derniers films complet et serie streaming complet en exclue et en streaming longue durée sans limitation en vf et vostfr. Vous êtes à deux clics de ne plus pourvoir vous passer de notre site de films en streaming.'
    )
    footer_description=models.TextField(
        blank=True,
        null=True,
        default='''Le Seul Site De Film Streaming En Hd 720p, Full Hd 1020p, Uh 4k Regardez Sans Limite Tous Les Films Et Séries Que Vous Desirez En Streaming Hd Sur (Papystreaming). Le Site N°1 Pour Voir Les Derniers Films Et Series En Streaming Vf Gratuitement, Sans Inscription Et Sans Pub. Visitez Notre Site De Streaming Maintenant Pour Retrouver Notre Collection Des Films Et Séries. Voir Votre Film En Français Préféré En Stream Complet. Du Grand Cinéma Classique Au Film D'auteur Contemporain, Regarder Les Meilleurs Films En Version Française.'''
    )
    tag=models.TextField(
        blank=True,
        null=True,
        default='''PapyStreaming Voir Film Site de streaming PapyStreaming VF Film streaming Regarder StreamingVF.'''
    )
    theme_color=models.CharField(max_length=255,blank=True,null=True,default='#4b57fc') # hex or rgb()
    background_color=models.CharField(max_length=255,blank=True,null=True,default='#111113') # hex or rgb()
    background_path=models.CharField(max_length=255,blank=True,null=True,default='/static/img/background.jpg') # hex or rgb()
    logo_path=models.CharField(max_length=255,blank=True,null=True,default='/static/img/logo.png') # hex or rgb()
    dmca=models.TextField(
        blank=True,
        null=True,
        default='''
            <br>
            PapyStreaming .forum respecte la propriété intellectuelle d'autrui et prend les questions de propriété intellectuelle très au sérieux et s’engage à répondre aux besoins des propriétaires de contenu tout en les aidant à gérer la publication de leur contenu en ligne.
            <br>
            <br>
            Si vous pensez que votre travail protégé par un droit d'auteur a été copié de manière à constituer une violation du droit d'auteur et qu'il est accessible sur ce site, vous pouvez en informer notre agent des droits d'auteur, comme indiqué dans la loi DMCA (Digital Millennium Copyright Act of 1998). Pour que votre réclamation soit valide en vertu de la DMCA, vous devez fournir les informations suivantes lors de l'envoi d'un avis d'infraction au droit d'auteur:
            <br>
            <br>
            Signature physique ou électronique d'une personne autorisée à agir au nom du titulaire du droit d'auteur Identification de l'œuvre protégée qui aurait été violée
            <br>
            <br>
            Identification du matériel présumé contrefaisant ou faisant l'objet de l'activité illicite et devant être enlevé
            <br>
            <br>
            Informations raisonnablement suffisantes pour permettre au fournisseur de services de contacter la partie plaignante, telles qu'une adresse, un numéro de téléphone et, le cas échéant, une adresse de courrier électronique
            <br>
            <br>
            Une déclaration indiquant que la partie plaignante "croit de bonne foi que l'utilisation du matériel de la manière incriminée n'est pas autorisée par le titulaire du droit d'auteur, son mandataire ou la loi"
            <br>
            <br>
            Une déclaration selon laquelle "les informations figurant dans la notification sont exactes" et "sous peine de parjure, la partie plaignante est autorisée à agir au nom du titulaire d'un droit exclusif prétendument violé"
            <br>
            <br>
            Les informations ci-dessus doivent être envoyées par notification écrite, télécopiée ou par courrier électronique à l'agent désigné suivant:
            <br>
            <br>
            Attention: bureau DMCA
            <br>
            <br>
            Contactez nous:
            <br>
            <br>
            sapystreamingdmca@gmail.com
            <br>
            <br>
            Ces informations ne doivent pas être interprétées comme des conseils juridiques. Pour plus d'informations sur les informations requises pour les notifications DMCA valides, voir 17 États-Unis d'Amérique. 512 (c) (3).
        '''
    )
    def save(self, *args, **kwargs):
        if self.name: self.name=self.name.lower()
        if self.domain_name: self.name=self.domain_name.lower()
        super().save(*args, **kwargs)
    def __str__(self):
        return self.domain_name
