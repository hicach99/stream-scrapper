from django.contrib import admin

from .models import *
from django.utils.html import format_html

# Keyword Start
class KeywordInline(admin.TabularInline):
    model = Keyword
    extra = 1
    fields = ('name',)
# Notification Start
class NotificationInline(admin.TabularInline):
    model = Notification
    extra = 0
    fields = ('content','created_on',)
    readonly_fields=('created_on',)
# Transaction Start
class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    fields = ('amount','status','created_on',)
    readonly_fields=('created_on',)
# OtherTitle Start
class OtherTitleInline(admin.TabularInline):
    model = OtherTitle
    extra = 0
    fields = ('title',)
# Link Start
class linkInline(admin.TabularInline):
    model = Link
    extra = 0
    fields = ('embed_link', 'version')
# Genre Start
class GenreAdmin(admin.ModelAdmin):
    exclude = ('movies',)
# Movie Start
class GenreMovieInline(admin.TabularInline):
    model = Genre.movies.through
    extra = 0
class CastMovieInline(admin.TabularInline):
    model = Cast.movies.through
    extra = 0
class DirectorMovieInline(admin.TabularInline):
    model = Director.movies.through
    extra = 0
class VideoMovieInline(admin.TabularInline):
    model = Video
    fields = ('site', 'name', 'key')
    extra = 0
class MovieAdmin(admin.ModelAdmin):
    search_fields = ['id','title','original_title']
    inlines = [OtherTitleInline, GenreMovieInline, KeywordInline, DirectorMovieInline,CastMovieInline,VideoMovieInline,linkInline]
    list_display = ('title','release_date','created_on','display_poster_path',)  # Add any other fields you want to display
    
    def display_poster_path(self, obj):
        
        if obj.poster_path:
            return format_html('<a href="/admin/app/movie/{}/change/"><img src="{}" height="150" style="border-radius: 10px;" /></a>',obj.id ,TmdbApi.original_images_url+obj.poster_path)
        else:
            return '(No image)'
    display_poster_path.short_description = 'Poster'
# Serie Start
class GenreSerieInline(admin.TabularInline):
    model = Genre.series.through
    extra = 0
class CastSerieInline(admin.TabularInline):
    model = Cast.series.through
    extra = 0
class DirectorSerieInline(admin.TabularInline):
    model = Director.series.through
    extra = 0
class VideoSerieInline(admin.TabularInline):
    model = Video
    extra = 0
    fields = ('site', 'name', 'key')
class SeasonSerieInline(admin.TabularInline):
    model = Season
    extra = 0
    fields = ('name', 'get_display_poster_path')
    readonly_fields = ('name', 'get_display_poster_path',)
    can_delete = False

    @staticmethod
    def get_display_poster_path(obj):
        if obj.poster_path:
            return format_html('<a href="/admin/app/season/{}/change/"><img src="{}" height="150" style="border-radius: 10px;" /></a>', obj.id, TmdbApi.original_images_url+obj.poster_path)
        else:
            return '(No image)'

    get_display_poster_path.short_description = 'Poster'

    @staticmethod
    def has_add_permission(self, request):
        return False

    @staticmethod
    def has_change_permission(self, request, obj=None):
        return False

    @staticmethod
    def has_delete_permission(self, request, obj=None):
        return False
    
class SerieAdmin(admin.ModelAdmin):
    search_fields = ['id','title','original_title']
    inlines = [OtherTitleInline, GenreSerieInline, KeywordInline, SeasonSerieInline,DirectorSerieInline,CastSerieInline,VideoSerieInline]
    list_display = ('title','release_date','created_on','display_poster_path',)  # Add any other fields you want to display
    readonly_fields = ('display_poster_path',)
    def display_poster_path(self, obj):
        
        if obj.poster_path:
            return format_html('<a href="/admin/app/serie/{}/change/"><img src="{}" height="150" style="border-radius: 10px;" /></a>',obj.id ,TmdbApi.original_images_url+obj.poster_path)
        else:
            return '(No image)'
    display_poster_path.short_description = 'Poster'
# Person Start
class PersonAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name','display_profile_path',)  # Add any other fields you want to display
    def display_profile_path(self, obj):
        
        if obj.profile_path:
            return format_html('<a href="/admin/app/person/{}/change/"><img src="{}" height="150" style="border-radius: 10px;" /></a>',obj.id ,TmdbApi.original_images_url+obj.profile_path)
        else:
            return '(No image)'
    display_profile_path.short_description = 'Profile'
# Season Start
class EpisodeSerieInline(admin.TabularInline):
    model = Episode
    extra = 0
    fields = ('episode_number', 'view')
    readonly_fields = ('episode_number','view',)
    def view(self, obj):
        return format_html('<a href="/admin/app/episode/{}/change/"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16"> <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/> <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/> </svg></a>',obj.id)
    view.short_description = 'View'
class SeasonAdmin(admin.ModelAdmin):
    search_fields = ['id','serie__title','serie__original_title','name']
    inlines = [EpisodeSerieInline, ]
    list_display = ('__str__','release_date','created_on','display_poster_path',)  # Add any other fields you want to display
    def display_poster_path(self, obj):
        if obj.poster_path:
            return format_html('<a href="/admin/app/season/{}/change/"><img src="{}" height="150" style="border-radius: 10px;" /></a>',obj.id ,TmdbApi.original_images_url+obj.poster_path)
        else:
            return '(No image)'
    display_poster_path.short_description = 'Poster'
# Episode Start
class EpisodeAdmin(admin.ModelAdmin):
    inlines = [linkInline,]

# Banners Admin
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title','release_date','created_on','enabled','display_poster_path',)  # Add any other fields you want to display
    def display_poster_path(self, obj):
        if obj.source.poster_path:
            return format_html('<a href="/admin/app/serie/{}/change/"><img src="{}" height="150" style="border-radius: 10px;" /></a>',obj.source.id ,TmdbApi.original_images_url+obj.source.poster_path)
        else:
            return '(No image)'
    display_poster_path.short_description = 'Poster'
    def title(self, obj): return obj.source.title
    def release_date(self, obj): return obj.source.release_date
    def created_on(self, obj): return obj.source.created_on
# platform Admin
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name','domain_name','url','display_theme_color','display_background_color')  # Add any other fields you want to display
    def display_theme_color(self, obj):
            return format_html('<a href="{}"><div style="border-radius: 10px;width:50px;height:50px;background-color:{};border: 2px solid white"></div></a>',obj.url ,obj.theme_color)
    display_theme_color.short_description = 'Theme Color'
    def display_background_color(self, obj):
            return format_html('<a href="{}"><div style="border-radius: 10px;width:50px;height:50px;background-color:{};border: 2px solid white"></div></a>',obj.url ,obj.background_color)
    display_background_color.short_description = 'Background Color'
# User Admin
class UserAdmin(admin.ModelAdmin):
    list_display = ('username','email','type','platform')  # Add any other fields you want to display
    inlines = [TransactionInline,NotificationInline]
class RequestAdmin(admin.ModelAdmin):
    list_display = ('tmdb_id','title','type','created_on')  # Add any other fields you want to display

# Display
admin.site.register(TmdbApi)
admin.site.register(Platform, PlatformAdmin)
admin.site.register(User,UserAdmin)
admin.site.register(Request,RequestAdmin)

admin.site.register(Serie, SerieAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Season, SeasonAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Episode, EpisodeAdmin)

admin.site.register(PopularMovie, BannerAdmin)
admin.site.register(UpcomingMovie, BannerAdmin)
admin.site.register(TopRatedMovie, BannerAdmin)
admin.site.register(PopularSerie, BannerAdmin)
admin.site.register(UpcomingSerie, BannerAdmin)
admin.site.register(TopRatedSerie, BannerAdmin)
