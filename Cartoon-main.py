import pickle
import os
import sys
import uuid
import psycopg2
from flask import Flask, request, redirect, send_from_directory, Response, render_template, url_for
from Show_Objects import cartoon_show_object, anime_show_object, show_object
from htmltemplate import Template
from PIL import Image
import base64

app = Flask(__name__)
app.secret_key = os.getenv('cartoon_secret_key')

Parent_Object = show_object()
Parent_Object.cartoon_dict = {}
Parent_Object.anime_dict = {}


def save_database():
    conn = psycopg2.connect(os.getenv('cartoon_database_url'))

    cursor = conn.cursor()
    cursor.execute('truncate "ShowPickle"')
    conn.commit()

    cursor.execute('INSERT INTO "ShowPickle"(cartoon_pickle_data) VALUES (%s)',
                   (psycopg2.Binary(pickle.dumps(Parent_Object)),))

    conn.commit()


# Load the Player list database
def load_database():
    try:
        global Parent_Object

        conn = psycopg2.connect(os.getenv('cartoon_database_url'))

        cursor = conn.cursor()
        cursor.execute('select cartoon_pickle_data from "ShowPickle" LIMIT 1')  #
        mypickle = cursor.fetchone()[0]
        Parent_Object = pickle.loads(mypickle)

    except TypeError as err:
        print("Unexpected error:", err)
        pass  # do nothing. no database to load
    except:
        pass  #this might happen if there's no schema deployed


def shrink_image(file):
    if file is not None and file.filename != '':
        image_to_shrink = Image.open(file)
        image_to_shrink.thumbnail((300, 300))
        image_to_shrink.save(file.filename)
        image_to_shrink.close()
        image_to_shrink = open(file.filename, 'rb')
        read_image = image_to_shrink.read()
        os.remove(file.filename)
        return read_image
    else:
        return None


@app.route('/initdb')
def setup_database():
    conn = psycopg2.connect(os.getenv('cartoon_database_url'))

    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE public."ShowPickle"
        (
            cartoon_pickle_data bytea, 
            anime_pickle_data bytea
        )
        with (
            OIDS = FALSE
        );
    ''')
    conn.commit()


@app.route('/cartoon_list', methods=['GET',])
def cartoon_list():
    load_database()
    cartoon_list_page = open(app.root_path + '/CartoonList.html').read()

    def render_Cartoon_template(node):
        node.Cartoon_Attribute.repeat(render_cartoonAtr, Parent_Object.cartoon_dict)



    def render_cartoonAtr(node, cartoonsection):

        if Parent_Object.cartoon_dict[cartoonsection].showimage is not None \
                and Parent_Object.cartoon_dict[cartoonsection].showimage != '':
            data64 = u'data:%s;base64, %s' % (
                'image/jpg', base64.encodebytes(Parent_Object.cartoon_dict[cartoonsection].showimage).decode('utf8'))
        else:
            data64 = None

        node.Cartoon_Title_Attribute.text = Parent_Object.cartoon_dict[cartoonsection].showname
        node.Cartoon_Title_Attribute.atts['href'] = Parent_Object.cartoon_dict[cartoonsection].showlink
        node.Cartoon_Edit_Attribute.atts['href'] = '/cartoon/' + str(Parent_Object.cartoon_dict[cartoonsection].id)
        node.Cartoon_Delete_Attribute.atts['href'] = '/cartoon/' + str(Parent_Object.cartoon_dict[cartoonsection].id) + '/delete'
        node.Cartoon_Logo_Attribute.atts['src'] = data64

    cartoon_list_template = Template(cartoon_list_page)
    return cartoon_list_template.render(render_Cartoon_template)


@app.route('/anime_list', methods=['GET',])
def anime_list():
    load_database()
    anime_list_page = open(app.root_path + "/AnimeList.html").read()


    def render_anime_template(node):
        node.Anime_Attribute.repeat(render_animeAtr, Parent_Object.anime_dict)

    def render_animeAtr(node, animesection):
        if Parent_Object.anime_dict[animesection].showimage is not None \
                and Parent_Object.anime_dict[animesection].showimage != '':
            data64 = u'data:%s;base64, %s' % (
                'image/jpg', base64.encodebytes(Parent_Object.anime_dict[animesection].showimage).decode('utf8'))
        else:
            data64 = None

        node.Anime_Title_Attribute.text = Parent_Object.anime_dict[animesection].showname
        node.Anime_Title_Attribute.atts['href'] = Parent_Object.anime_dict[animesection].showlink
        node.Anime_Edit_Attribute.atts['href'] = '/anime/' + str(Parent_Object.anime_dict[animesection].id)
        node.Anime_Delete_Attribute.atts['href'] = '/anime/' +str(Parent_Object.anime_dict[animesection].id) + '/delete'
        node.Anime_Logo_Attribute.atts['src'] = data64


    anime_list_template = Template(anime_list_page)
    return anime_list_template.render(render_anime_template)


@app.route('/<path:path>')
def send_js(path):
    return send_from_directory('', path)


@app.route('/cartoon/<id>', methods=['GET',])
def get_cartoon(id):
    global Parent_Object
    load_database()

    id_as_uuid = uuid.UUID(id)
    cartoon_object_from_dictionary = Parent_Object.cartoon_dict[id_as_uuid]

    if cartoon_object_from_dictionary.showimage is not None\
            and cartoon_object_from_dictionary.showimage != '':
        data64 = u'data:%s;base64, %s' % (
            'image/jpg', base64.encodebytes(cartoon_object_from_dictionary.showimage).decode('utf8'))
    else:
        data64 = None

    edit_page = open('Cartoon_Edit.html').read()

    def render_cartoon(node, cartoon_object):
        node.ActionPathAtr.atts['action'] = '/cartoon/' + str(id_as_uuid) + '/update'
        node.ActionPathAtr.Cartoon_Link_Attribute.atts['value'] = cartoon_object.showlink
        node.ActionPathAtr.Cartoon_Title_Attribute.atts['value'] = cartoon_object.showname
        node.ActionPathAtr.DisplayImgAtr.atts['src'] = data64

    cartoon_template = Template(edit_page)
    return cartoon_template.render(render_cartoon, cartoon_object_from_dictionary)


@app.route('/anime/<id>', methods=['GET',])
def get_anime(id):
    global Parent_Object
    load_database()

    id_as_uuid = uuid.UUID(id)
    anime_object_from_dictionary = Parent_Object.anime_dict[id_as_uuid]

    if anime_object_from_dictionary.showimage is not None\
            and anime_object_from_dictionary.showimage != '':
        data64 = u'data:%s;base64, %s' % (
            'image/jpg', base64.encodebytes(anime_object_from_dictionary.showimage).decode('utf8'))

    else:
        data64 = None

    edit_page = open('Anime_Edit.html').read()

    def render_anime(node, anime_object):
        node.ActionPathAtr.atts['action'] = '/anime/' + str(id_as_uuid) + '/update'
        node.ActionPathAtr.Anime_Link_Attribute.atts['value'] = anime_object.showlink
        node.ActionPathAtr.Anime_Title_Attribute.atts['value'] = anime_object.showname
        node.ActionPathAtr.DisplayImgAtr.atts['src'] = data64

    cartoon_template = Template(edit_page)
    return cartoon_template.render(render_anime, anime_object_from_dictionary)


@app.route('/cartoon/<id>/delete')
def delete_cartoon(id):
    global Parent_Object
    load_database()
    id_as_uuid = uuid.UUID(id)
    del Parent_Object.cartoon_dict[id_as_uuid]
    save_database()
    return redirect('/cartoon_list')


@app.route('/anime/<id>/delete')
def delete_anime(id):
    global Parent_Object
    load_database()
    id_as_uuid = uuid.UUID(id)
    del Parent_Object.anime_dict[id_as_uuid]
    save_database()
    return redirect('/anime_list')


@app.route('/cartoon/<id>/update', methods=['POST',])
def update_cartoon(id):
    global Parent_Object
    load_database()

    id_as_uuid = uuid.UUID(id)

    cartoon_to_update = Parent_Object.cartoon_dict[id_as_uuid]

    try:
        file = request.files['Image_Input']
    except:
        file = None

    cartoon_to_update.showname = request.form['Cartoon_Title_Input']

    if file is not None:
        cartoon_to_update.showimage = shrink_image(file)

    cartoon_to_update.showlink = request.form['Cartoon_Link_Input']

    Parent_Object.cartoon_dict[id_as_uuid] = cartoon_to_update
    save_database()
    return redirect('/')


@app.route('/anime/<id>/update', methods=['POST',])
def update_anime(id):
    global Parent_Object
    load_database()

    id_as_uuid = uuid.UUID(id)

    anime_to_update = Parent_Object.anime_dict[id_as_uuid]

    try:
        file = request.files['Image_Input']
    except:
        file = None

    anime_to_update.showname = request.form['Anime_Title_Input']

    if file is not None:
        anime_to_update.showimage = shrink_image(file)
    anime_to_update.showlink=request.form['Anime_Link_Input']

    Parent_Object.anime_dict[id_as_uuid] = anime_to_update
    save_database()
    return redirect('/')


@app.route('/')
def home():
    this_folder = os.path.dirname(os.path.abspath(__file__))
    home_page = os.path.join(this_folder, 'Home.html')
    with open(home_page) as home:
        list_page = open(home_page).read()
        return list_page


@app.route('/cartoon/new/', methods=['POST',])
def add_cartooon():
    try:
        file = request.files['Image_Input']
    except:
        file = None

    # instantiate a new show object and populate it from request.form
    New_Cartoon = cartoon_show_object(
        showname=request.form['Cartoon_Title_Input'],
        showimage=shrink_image(file),
        showlink=request.form['Cartoon_Link_Input'])

    Parent_Object.cartoon_dict[New_Cartoon.id] = New_Cartoon
    save_database()
    return redirect('/')


@app.route('/cartoon/new/', methods=['GET',])
def get_add_cartooon_form():

    def render_cartoon_page(node):
        node.ActionPathAtr.atts['action'] = '/cartoon/new/'

    this_folder = os.path.dirname(os.path.abspath(__file__))
    add_cartoon_page = os.path.join(this_folder, 'Cartoon_Edit.html')
    cartoon_template = Template(open(add_cartoon_page).read())
    return cartoon_template.render(render_cartoon_page)
    #return open(add_cartoon_page).read()


@app.route('/anime/new/', methods=['GET',])
def get_add_anime_form():

    def render_anime_page(node):
        node.ActionPathAtr.atts['action'] = '/anime/new/'

    this_folder = os.path.dirname(os.path.abspath(__file__))
    add_anime_page = os.path.join(this_folder, 'Anime_Edit.html')
    anime_template = Template(open(add_anime_page).read())
    return anime_template.render(render_anime_page)
    #return open(add_anime_page).read()


@app.route('/anime/new/', methods=['POST',])
def add_anime():
    try:
        file = request.files['Image_Input']
    except:
        file = None

        # instantiate a new show object and populate it from request.form
    New_Anime = anime_show_object(
        showname=request.form['Anime_Title_Input'],
        showimage=shrink_image(file),
        showlink=request.form['Anime_Link_Input'])

    Parent_Object.anime_dict[New_Anime.id] = New_Anime
    save_database()
    return redirect('/')


@app.route('/search/', methods=['POST', ])
def search():
    load_database()
    search_result_list2 = {}

    for animekey, animeitem in Parent_Object.anime_dict.items():
        if animeitem.showname == request.form['searchbox']:
            search_result_list2[animekey] = animeitem

    for cartoonkey, cartoonitem in Parent_Object.cartoon_dict.items():
        if cartoonitem.showname == request.form['searchbox']:
            search_result_list2[cartoonkey] = cartoonitem

    this_folder = os.path.dirname(os.path.abspath(__file__))
    search_results_page = os.path.join(this_folder, 'Search_Results.html')

    def render_anime_template(node):
        node.Anime_Attribute.repeat(render_animeAtr, search_result_list2)

    def render_animeAtr(node, animesection):
        if search_result_list2[animesection].showimage is not None \
                and search_result_list2[animesection].showimage != '':
            data64 = u'data:%s;base64, %s' % (
                'image/jpg', base64.encodebytes(search_result_list2[animesection].showimage).decode('utf8'))
        else:
            data64 = None

        node.Anime_Logo_Attribute.atts['src'] = data64
        node.Anime_Title_Attribute.text = search_result_list2[animesection].showname
        node.Anime_Title_Attribute.atts['href'] = search_result_list2[animesection].showlink
        if type(search_result_list2[animesection]) == anime_show_object:
            node.Anime_Edit_Attribute.atts['href'] = '/anime/' + str(search_result_list2[animesection].id)
        elif type(search_result_list2[animesection]) == cartoon_show_object:
            node.Anime_Edit_Attribute.atts['href'] = '/cartoon/' + str(search_result_list2[animesection].id)


    search_template = Template(open(search_results_page).read())
    return search_template.render(render_anime_template)


if __name__ == '__main__':
    load_database()
    app.run(debug=True)
