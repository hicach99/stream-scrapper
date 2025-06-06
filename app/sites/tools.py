import re
import traceback
from app.models import Movie, Serie
from django.conf import settings

def get_exception_details(e : Exception):
    tb = traceback.extract_tb(e.__traceback__)
    return tb[-1].filename, tb[-1].lineno
def add_message_to_file(file_path, message):
    try:
        with open(settings.BASE_DIR / file_path, 'a') as file:
            file.write(message + '\n')
    except FileNotFoundError:
        with open(settings.BASE_DIR / file_path, 'w') as file:
            file.write(message + '\n')
    except Exception as e:
        print(e)

def is_list(variable):
    if isinstance(variable, list):
        return True
    else:
        return False

def process_string(input_string):
    year_match = re.search(r"\((\d{4})\)| - (\d{4})", input_string)
    
    additional_text_match = re.search(r"\((.*?)\)| - ([^-]+)$", input_string)
    
    main_text = re.sub(r"\(.*?\)| - \d{4}| - [^-]+$", "", input_string).strip()
    
    if year_match:
        year = year_match.group(1) if year_match.group(1) else year_match.group(2)
    else:
        year = None
    
    if additional_text_match:
        additional_text = additional_text_match.group(1) if additional_text_match.group(1) else additional_text_match.group(2)
    else:
        additional_text = None
    
    return main_text, year, additional_text

def remove_symbols(input_string):
    clean_string = re.sub(r'[^a-zA-Z0-9.:\s]', '', input_string)
    return clean_string
def get_word_with_highest_value(dictionary):
    if not dictionary: 
        return None
    return max(dictionary, key=dictionary.get)
def select_highest_match(strings, original):
    map_dic={}
    for word in strings: map_dic[word]=0
    original_parts=remove_symbols(original).split(' ')
    for o_word in original_parts:
        for word in strings:
            if o_word in remove_symbols(word):
                map_dic[word]+=1
    highest=get_word_with_highest_value(map_dic)
    return strings.index(highest), map_dic[highest], highest
def search_select_movie(title:str,d_year:str) -> Movie:
    title,year,sig=process_string(title)
    old_movies=Movie.search_tmdb(title)
    movies = []
    for m in old_movies:
        try:
            if d_year in m.release_date:
                movies.append(m)
        except:
            pass
    for m in old_movies:
        try:
            if year and (year in m.release_date) and (m not in movies):
                movies.append(m)
        except:
            pass
    if not movies: movies=old_movies
    if movies:
        try:
            titles=[]
            t_m = []
            for movie in movies:
                try:
                    titles.append(movie.title)
                    t_m.append(movie)
                except:pass
            original_titles=[]
            ot_m = []
            for movie in movies:
                try:
                    original_titles.append(movie.original_title)
                    ot_m.append(movie)
                except:pass
            res=select_highest_match(titles, title)
            o_res=select_highest_match(original_titles, title)
            if res[1]>o_res[1]:
                return t_m[res[0]]
            return ot_m[o_res[0]]
        except: pass
    return None
def search_select_serie(title:str,nb_seasons:int) -> Serie:
    title,year,sig=process_string(title)
    a_series=[]
    for s in Serie.search_tmdb(title):
        try:
            a_series.append(Serie.get_tmdb(s.id))
        except:
            pass
    series = []
    for s in a_series:
        try:
            if (nb_seasons==18 and int(s.number_of_seasons)>=18) or (nb_seasons<18 and int(s.number_of_seasons) == nb_seasons):
                series.append(s)
        except: pass
    if not series:
        for s in a_series:
            try:
                if (nb_seasons==18 and int(s.number_of_seasons)>=18) or (nb_seasons<18 and int(s.number_of_seasons) in [nb_seasons, nb_seasons+1]):
                    series.append(s)
            except: pass
    if year:
        series = [serie for serie in series  if year in serie.first_air_date]
    if not series:
        series = a_series
    if series:
        try:
            titles=[]
            t_m = []
            for serie in series:
                try:
                    titles.append(serie.name)
                    t_m.append(serie)
                except:pass
            original_titles=[]
            ot_m = []
            for serie in series:
                try:
                    original_titles.append(serie.original_name)
                    ot_m.append(serie)
                except:pass
            res=select_highest_match(titles, title)
            o_res=select_highest_match(original_titles, title)
            if res[1]>o_res[1]:
                return t_m[res[0]]
            return ot_m[o_res[0]]
        except: pass
    return None
