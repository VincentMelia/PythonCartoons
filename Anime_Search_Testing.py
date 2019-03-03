from Show_Objects import anime_show_object
import re

Anime1 = anime_show_object()
Anime2 = anime_show_object()
Anime3 = anime_show_object()

Anime1.showname = 'anime1name'
Anime1.showlink = 'anime1link'

Anime2.showname = 'anime2name'
Anime2.showlink = 'anime2link'

Anime3.showname = 'anime3name'
Anime3.showlink = 'anime3link'

AnimeList = [Anime1, Anime2, Anime3]


def AnimeSearch(animesearchtext):
    search_result_list = []
    for animeitem in AnimeList:
        if animeitem.showname == animesearchtext:
            search_result_list.append(animeitem)
    pass

AnimeSearch('anime')


def AnimeWildCardSearch(animesearchtext):
    search_result_list = []
    for animeitem in AnimeList:
        if animeitem.showname == animesearchtext:
            search_result_list.append(animeitem)
    pass
    return search_result_list


print(AnimeWildCardSearch('anime3name'))

re.search('(.*)anime(.*)', AnimeList[0].showname).group(1)
