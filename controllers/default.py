# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
import re
import random

stoplist = [
    "",
    "The", "the",
    "is", "an"
    "to", "at",
    "of", "in",
    "and",
]

def get_user_name_from_email(email):
    """Returns a string corresponding to the user first and last names,
    given the user email."""
    u = db(db.auth_user.email == email).select().first()
    if u is None:
        return 'None'
    else:
        return ' '.join([u.first_name, u.last_name])


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    if auth.user_id is not None: ()
    trl_list = []
    i = 0
    for row in db().select(db.trailers_metadata.ALL):
        trl_list.append(row)
        i += 1
    movie_list = []
    j = 0
    for row in db().select(db.movie_metadata.ALL):
        movie_list.append(row)
        j += 1
    randm1 = []
    randm2 = []
    randm3 = []
    for x in range(0, 3):
        randm1.append(movie_list[random.randint(0, j - 1)])
        randm2.append(movie_list[random.randint(0, j - 1)])
        randm3.append(movie_list[random.randint(0, j - 1)])
    randt = trl_list[random.randint(0, i - 1)]
    genre = ['Action', 'Adventure', 'Fantasy', 'Sci-Fi', 'Thriller', 'Documentary', 'Romance', 'Animation', 'Comedy',
             'Family', 'Musical', 'Mystery', 'Western', 'Drama', 'History', 'Sport', 'Crime', 'Horror', 'War',
             'Biography', 'Music', 'Game-Show', 'Reality-TV', 'News', 'Short', 'Film-Noir']
    return dict(trl=trl_list, rant=randt, ranm1=randm1, ranm2=randm2, ranm3=randm3, genres=genre)


@auth.requires_signature()
def preferences():
    """Suggests movie, add like movie to database, dislike movie to database:
    """
    rows = db().select(db.movie_metadata.ALL, limitby=(0, 100))
    return dict(rows=rows)


def page():
    movie_id = 5
    movie = db(db.movie_metadata.movie_id == movie_id).select()
    return dict(movie=movie)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    # Redirects user to users preference page
    auth.settings.login_next = URL('default', 'preferences')
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


def directors():
    return dict()


def genres():
    genre = request.args[0]
    rows = db(db.movie_metadata.genres.contains(genre)).select()
    return dict(rows=rows)


def popular():
    rows = db(db.movie_metadata.movie_facebook_likes).select(limitby=(0, 25), orderby=~db.movie_metadata.movie_facebook_likes)
    return dict(rows=rows)


def top():
    rows = db(db.movie_metadata.imdb_score).select(limitby=(0, 25), orderby=~db.movie_metadata.imdb_score)
    return dict(rows=rows)


def get_movies():
    search_string = request.vars.q.strip()
    rows = db().select(db.test_db.ALL, limitby=(0, 100))
    movie_list = []
    sublist = []
    title_list = []
    original_list = []

    #Starting algorithm, start by finding all words with a size greater than 2
    for r in rows:
        append_list = re.findall(r'[A-z0-9][A-z0-9]+', r.movie_title)
        if len(append_list):
            title_list.append(append_list)
            original_list.append(r.movie_title)

    i = 0
    removal = 0

    #each title in the title is another title
    for title in title_list:
        k = 0

        #this code changes all words to lower case if not already, makes the word non-plural. No I can't actually
        #tell if it's plural, but as long as I apply the same technique to incoming search terms the result is the same
        for word in title:
            title[k] = word.lower()
            if title[k][-1] == 's' and title[k][-2] != 's':
                title[k] = title[k][:-1]
            k+=1

        s_word = 0
        removal = 0

        #This code removes useless words that can't be used as keywords. The funny stuff with the while loop is because
        #of the array removal causing shenanagins
        while s_word < len(title):
            for stop_word in stoplist:
                if title[s_word] == stop_word:
                    title.remove(title[s_word])
                    removal = 1
            if removal:
                removal = 0
            else:
                s_word += 1


    #This code starts both the query parsing as well as the scoring algorithm
    #good shit right here
    if request.vars.q.strip():
        high_list = []
        high_original = []

        #parse the search terms using the same methods as the titles to ensure compaitbility
        search_list = [x for x in re.findall(r'[A-z0-9][A-z0-9]+', request.vars.q)]

        i = 0
        for word in search_list:
            search_list[i] = word.lower()
            if search_list[i][-1] == 's' and search_list[i][-2] != 's':
                search_list[i] = search_list[i][:-1]
            i += 1

        s_word = 0
        removal = 0
        # This code removes useless words that can't be used as keywords, just like the one before
        while s_word < len(search_list):
            for stop_word in stoplist:
                if search_list[s_word] == stop_word:
                    search_list.remove(search_list[s_word])
                    removal = 1
            if removal:
                removal = 0
            else:
                s_word += 1

        highest_score = 0
        index = 0
        for list in title_list:
            search_match = 0
            for title_word in list:
                for search_word in search_list:
                    if search_word == title_word:
                        search_match += 1

            # This is the actual algorithm,
            # score =        [# of matched words]              [# of matched words]
            #              -------------------------   +  ------------------------------
            #              2 x [# of searched words]      2 x [# of words in movie title]
            search_score = float(search_match) / (len(search_list) * 2) + float(search_match) / (len(list) * 2)

            #Scorekeeping
            if search_score > highest_score:
                #print(original_list[index])
                sublist = []
                sublist.append(original_list[index])
                sublist.append(search_score)
                high_original = [sublist] + high_original
                sublist = []

                highest_score = search_score
            elif search_score > 0.3:
                #print(original_list[index])
                sublist = []
                sublist.append(original_list[index])
                sublist.append(search_score)
                high_original.append(sublist)
            sublist = []
            index += 1
            #end for loop
        for item in high_original:
            sublist = []
            r = db(db.test_db.movie_title == item[0]).select().first()
            sublist.append(r.movie_title)
            sublist.append(r.director_name)
            sublist.append(r.imdb_score)
            sublist.append(r.genres)
            sublist.append(r.synopsis)
            sublist.append(r.content_rating)
            sublist.append(r.poster_url)
            sublist.append(r.movie_imdb_link)

            movie_list.append(sublist)

    else:
        for r in rows:
            #append items to the list of lists of lists of lists of lists of lists
            sublist.append(r.movie_title)
            sublist.append(r.director_name)
            sublist.append(r.imdb_score)
            sublist.append(r.genres)
            sublist.append(r.synopsis)
            sublist.append(r.content_rating)
            sublist.append(r.poster_url)
            sublist.append(r.movie_imdb_link)

            movie_list.append(sublist)
            sublist = []

    return response.json(dict(movie_list=movie_list))

def movies():
    return dict()

