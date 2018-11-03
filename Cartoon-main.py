import pickle
import os
import sys
import uuid
import psycopg2
from flask import Flask, request, redirect, send_from_directory, Response, render_template, url_for
from Show_Objects import cartoon_show_object, anime_show_object, show_object
from htmltemplate import Template
from PIL import Image

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
        node.Cartoon_Title_Attribute.text = Parent_Object.cartoon_dict[cartoonsection].showname
        node.Cartoon_Title_Attribute.atts['href'] = Parent_Object.cartoon_dict[cartoonsection].showlink
        node.Cartoon_Edit_Attribute.atts['href'] = '/cartoon/' + str(Parent_Object.cartoon_dict[cartoonsection].id)

    cartoon_list_template = Template(cartoon_list_page)
    return cartoon_list_template.render(render_Cartoon_template)


@app.route('/anime_list', methods=['GET',])
def anime_list():
    load_database()
    anime_list_page = open(app.root_path + "/static/AnimeList.html").read()
    # anime_list_page = open(url_for('static', filename='AnimeList.html')).read()

    def render_anime_template(node):
        node.Anime_Attribute.repeat(render_animeAtr, Parent_Object.anime_dict)

    def render_animeAtr(node, animesection):
        node.Anime_Title_Attribute.text = Parent_Object.anime_dict[animesection].showname
        node.Anime_Title_Attribute.atts['href'] = Parent_Object.anime_dict[animesection].showlink
        node.Anime_Edit_Attribute.atts['href'] = '/anime/' + str(Parent_Object.anime_dict[animesection].id)

    anime_list_template = Template(anime_list_page)
    return anime_list_template.render(render_anime_template)


@app.route('/<path:path>' )
def send_js(path):
    return send_from_directory('', path)


@app.route('/cartoon/<id>', methods=['GET',])
def get_cartoon(id):
    global Parent_Object
    load_database()

    id_as_uuid = uuid.UUID(id)
    cartoon_object_from_dictionary = Parent_Object.cartoon_dict[id_as_uuid]

    edit_page = open('Cartoon_Edit.html').read()

    def render_cartoon(node, cartoon_object):
        node.Cartoon_Link_Attribute.atts['value'] = cartoon_object.showlink
        node.Cartoon_Title_Attribute.atts['value'] = cartoon_object.showname

    cartoon_template = Template(edit_page)
    return cartoon_template.render(render_cartoon, cartoon_object_from_dictionary)


@app.route('/anime/<id>', methods=['GET',])
def get_anime(id):
    global Parent_Object
    load_database()

    id_as_uuid = uuid.UUID(id)
    anime_object_from_dictionary = Parent_Object.anime_dict[id_as_uuid]

    edit_page = open('Anime_Edit.html').read()

    def render_anime(node, anime_object):
        node.Anime_Link_Attribute.atts['value'] = 'http://www.microsoft.com'#anime_object.showlink
        node.Anime_Title_Attribute.atts['value'] = anime_object.showname

    cartoon_template = Template(edit_page)
    return cartoon_template.render(render_anime, anime_object_from_dictionary)



@app.route('/cartoon/<id>/delete')
def delete_cartoon():
    pass


@app.route('/anime/<id>/delete')
def delete_anime():
    pass


@app.route('/cartoon/<id>/update')
def update_cartoon():

    cartoon_to_update = Parent_Object.cartoon_dict[id]

    try:
        file = request.files['Image_Input']
    except:
        file = None

    if file is not None and file.filename != '':
        uploaded_image = Image.open(file)
        uploaded_image.thumbnail((500, 500))
        uploaded_image.save(file.filename)
        uploaded_image.close()
        uploaded_image = open(file.filename, 'rb')

        cartoon_to_update.showname = request.form['Cartoon_Title_Input']
        cartoon_to_update.showimage = uploaded_image.read()
        cartoon_to_update.showlink = request.form['Cartoon_Link_Input']
    else:
        cartoon_to_update.showname = request.form['Cartoon_Title_Input']
        cartoon_to_update.showlink = request.form['Cartoon_Link_Input']

    Parent_Object.cartoon_dict[id] = cartoon_to_update
    save_database()
    return redirect('/')


@app.route('/anime/<id>/update')
def update_anime():
    anime_to_update = Parent_Object.anime_dict[id]

    try:
        file = request.files['Image_Input']
    except:
        file = None

    if file is not None and file.filename != '':
        uploaded_image = Image.open(file)
        uploaded_image.thumbnail((500, 500))
        uploaded_image.save(file.filename)
        uploaded_image.close()
        uploaded_image = open(file.filename,'rb')

        anime_to_update.showname = request.form['Anime_Title_Input']
        anime_to_update.showimage = uploaded_image.read()
        anime_to_update.showlink=request.form['Anime_Link_Input']
    else:
        anime_to_update.showname=request.form['Anime_Title_Input']
        anime_to_update.showlink=request.form['Anime_Link_Input']

    Parent_Object.anime_dict[id] = anime_to_update
    save_database()
    return redirect('/')

@app.route('/')
def home():
    this_folder = os.path.dirname(os.path.abspath(__file__))
    home_page = os.path.join(this_folder, 'Home.html')
    with open(home_page) as home:
        list_page = open(home_page).read()
        return list_page


@app.route('/cartoon/new', methods=['POST',])
def add_cartooon():
    try:
        file = request.files['Image_Input']
    except:
        file = None

    if file is not None and file.filename != '':
        uploaded_image = Image.open(file)
        uploaded_image.thumbnail((500, 500))
        uploaded_image.save(file.filename)
        uploaded_image.close()
        uploaded_image=open(file.filename,'rb')

    # instantiate a new show object and populate it from request.form
        New_Cartoon = cartoon_show_object(
            showname=request.form['Cartoon_Title_Input'],
            showimage=uploaded_image.read(),
            showlink=request.form['Cartoon_Link_Input'])
    else:
        New_Cartoon = cartoon_show_object(
            showname=request.form['Cartoon_Title_Input'],
            showlink=request.form['Cartoon_Link_Input'])

    Parent_Object.cartoon_dict[New_Cartoon.id] = New_Cartoon
    save_database()
    return redirect('/')


@app.route('/cartoon/new', methods=['GET',])
def get_add_cartooon_form():
    this_folder = os.path.dirname(os.path.abspath(__file__))
    add_cartoon_page = os.path.join(this_folder, 'Cartoon_Edit.html')
    return open(add_cartoon_page).read()


@app.route('/anime/new', methods=['POST',])
def add_anime():
    try:
        file = request.files['Image_Input']
    except:
        file = None

    if file is not None and file.filename != '':
        uploaded_image = Image.open(file)
        uploaded_image.thumbnail((500, 500))
        uploaded_image.save(file.filename)
        uploaded_image.close()
        uploaded_image=open(file.filename,'rb')

        # instantiate a new show object and populate it from request.form
        New_Anime = anime_show_object(
            showname=request.form['Anime_Title_Input'],
            showimage=uploaded_image.read(),
            showlink=request.form['Anime_Link_Input'])
    else:
        New_Anime=anime_show_object(
            showname=request.form['Anime_Title_Input'],
            showlink=request.form['Anime_Link_Input'])

    Parent_Object.anime_dict[New_Anime.id] = New_Anime
    save_database()
    return redirect('/')


@app.route('/anime/new', methods=['GET',])
def get_add_anime_form():
    this_folder = os.path.dirname(os.path.abspath(__file__))
    add_anime_page = os.path.join(this_folder, 'Anime_Edit.html')
    return open(add_anime_page).read()


if __name__ == '__main__':
    load_database()
    app.run(debug=True)
