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
    # Extract the year within parentheses using regex
    year_match = re.search(r"\((\d{4})\)", input_string)
    
    # Extract the additional text within parentheses using regex
    additional_text_match = re.search(r"\((.*?)\)", input_string)
    
    # Extract the main text excluding parentheses and additional text
    main_text = re.sub(r"\(.*?\)", "", input_string).strip()
    
    if year_match:
        year = year_match.group(1)
    else:
        year = None
    
    if additional_text_match:
        additional_text = additional_text_match.group(1)
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
    movies=old_movies=Movie.search_tmdb(title)
    movies=[m for m in movies if d_year in m.release_date] 
    if not movies: movies=old_movies
    if year:
        movies = [movie for movie in movies if year in movie.release_date]
        if not movies: movies=old_movies
    if movies:
        titles=[movie.title for movie in movies]
        original_titles=[movie.original_title for movie in movies]
        res=select_highest_match(titles, title)
        o_res=select_highest_match(original_titles, title)
        if res[1]>o_res[1]:
            return movies[res[0]]
        return movies[o_res[0]]
    return None
def search_select_serie(title:str,season_number:int) -> Serie:
    title,year,sig=process_string(title)
    series=[Serie.get_tmdb(s.id) for s in Serie.search_tmdb(title)]
    series=[s for s in series if s.number_of_seasons>=season_number]
    if year:
       series = [serie for serie in series  if year in serie.first_air_date]
    if series:
        titles=[serie.name for serie in series]
        original_titles=[serie.original_name for serie in series]
        res=select_highest_match(titles, title)
        o_res=select_highest_match(original_titles, title)
        if res[1]>o_res[1]:
            return series[res[0]]
        return series[o_res[0]]
    return None
