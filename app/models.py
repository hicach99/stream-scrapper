import random
from django.db import models
from tmdbv3api import TMDb, Movie as Tmdb_Movie,TV as Tmdb_Serie

class TmdbApi(models.Model):
    api_keys=[
    'fb7bb23f03b6994dafc674c074d01761',
    'e55425032d3d0f371fc776f302e7c09b',
    '8301a21598f8b45668d5711a814f01f6',
    '8cf43ad9c085135b9479ad5cf6bbcbda',
    'da63548086e399ffc910fbc08526df05',
    '13e53ff644a8bd4ba37b3e1044ad24f3',
    '269890f657dddf4635473cf4cf456576',
    'a2f888b27315e62e471b2d587048f32e',
    '8476a7ab80ad76f0936744df0430e67c',
    '5622cafbfe8f8cfe358a29c53e19bba0',
    'ae4bd1b6fce2a5648671bfc171d15ba4',
    '257654f35e3dff105574f97fb4b97035',
    '2f4038e83265214a0dcd6ec2eb3276f5',
    '9e43f45f94705cc8e1d5a0400d19a7b7',
    'af6887753365e14160254ac7f4345dd2',
    '06f10fc8741a672af455421c239a1ffc',
    'fb7bb23f03b6994dafc674c074d01761',
    '09ad8ace66eec34302943272db0e8d2c'
    ]
    original_images_url='https://image.tmdb.org/t/p/original'
tmdb = TMDb()
tmdb.language = 'fr'
movie_getter = Tmdb_Movie()
serie_getter = Tmdb_Serie()

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
                    person=Person.objects.create(id=c.id,name=c.name,profile_path=c.profile_path)
                    person.save()
                cast=cls.objects.create(person=person, character=c.character)
            cast.save()
            if movie:
                cast.movies.add(movie)
            elif serie:
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
                        person.save()
                    director=cls.objects.create(person=person)
                director.save()
                director.movies.add(movie)
            elif serie:
                try:
                    director=cls.objects.get(person__id=d.id)
                except:
                    try:
                        person=Person.objects.get(id=d.id)
                    except:
                        person=Person.objects.create(id=d.id,name=d.name,profile_path=d.profile_path)
                        person.save()
                    director=cls.objects.create(person=person)
                director.save()
                director.series.add(serie)
    def __str__(self):
        return self.person.name

class Movie(models.Model):
    id = models.IntegerField(primary_key=True)
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
    created_on = models.DateField(auto_now_add=True,null=True)
    quality = models.CharField(max_length=255,blank=True,null=True)
    def set_movie_details(self,movie):
        try:
            self.adult = movie.adult
            self.title = movie.title
            self.runtime = movie.runtime
            self.original_title = movie.original_title
            self.overview = movie.overview
            self.countries = ', '.join([i['iso_3166_1'] for i in movie.production_countries])
            self.release_date = movie.release_date
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
            tmdb.api_key = random.choice(TmdbApi.api_keys)
            movie = movie_getter.details(self.id)
            self.set_movie_details(movie)
            self.generated=True
            super().save(*args, **kwargs)
            curr_movie=Movie.objects.get(id=self.id)
            Genre.save_if_not_exists(movie.genres,movie=curr_movie)
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
        tmdb.api_key = random.choice(TmdbApi.api_keys)
        return movie_getter.search(query)
    @classmethod
    def get_tmdb(cls,id:int):
        tmdb.api_key = random.choice(TmdbApi.api_keys)
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
    created_on = models.DateField(auto_now_add=True,null=True)
    def set_serie_details(self,serie):
        try:
            self.adult = serie.adult
            self.in_production = serie.in_production
            self.title = serie.name
            self.runtime = serie.episode_run_time[0] if serie.episode_run_time else None
            self.original_title = serie.original_name
            self.overview = serie.overview
            self.countries = ', '.join(serie.origin_country)
            self.release_date = serie.first_air_date
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
            tmdb.api_key = random.choice(TmdbApi.api_keys)
            serie = serie_getter.details(self.id)
            self.set_serie_details(serie)
            self.generated=True
            super().save(*args, **kwargs)
            curr_serie=Serie.objects.get(id=self.id)
            Genre.save_if_not_exists(serie.genres,serie=curr_serie)
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
        tmdb.api_key = random.choice(TmdbApi.api_keys)
        return serie_getter.search(query)
    @classmethod
    def get_tmdb(cls,id:int):
        tmdb.api_key = random.choice(TmdbApi.api_keys)
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
    created_on = models.DateField(auto_now_add=True,null=True)
    serie = models.ForeignKey('Serie', related_name='seasons', blank=True, on_delete=models.CASCADE,null=True)
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
    created_on = models.DateField(auto_now_add=True,null=True)
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
    created_on = models.DateField(auto_now_add=True,null=True)
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
            if movie:
                genre.movies.add(movie)
            elif serie:
                genre.series.add(serie)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
class OtherTitle(models.Model):
    title = models.CharField(max_length=255,blank=True,null=True)
    movie = models.ForeignKey(Movie, related_name='other_titles', on_delete=models.CASCADE, null=True, blank=True)
    serie = models.ForeignKey(Serie, related_name='other_titles', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.title