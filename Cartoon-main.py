import pickle
import os
import uuid
import psycopg2
from Configuration import ShowDatabase
from flask import Flask, request, redirect, send_from_directory, Response, render_template
from Show_Objects import cartoon_show_object, anime_show_object
from htmltemplate import Template

app = Flask(__name__)
app.secret_key = os.getenv('cartoon_secret_key')

Cartoondict = {}

Animedict = {}

def save_database():
    Database_file = open(ShowDatabase, 'wb')
    pickle.dump(Cartoondict, Database_file)
    Database_file.close()

    Database_file = open(ShowDatabase, 'rb')
    Database_file_pickle = Database_file.read()
    Database_file.close()

    conn = psycopg2.connect(os.getenv('cartoon_database_url'))

    cursor = conn.cursor()
    cursor.execute('truncate "ShowPickle"')
    conn.commit()

    cursor.execute('INSERT INTO "ShowPickle"(cartoon_pickle_data) VALUES (%s)',
                    (psycopg2.Binary(Database_file_pickle),))
    conn.commit()


# Load the Player lst database
def load_database():
    try:
        global Cartoondict

        conn = psycopg2.connect(os.getenv('cartoon_database_url'))

        cursor = conn.cursor()
        cursor.execute('select cartoon_pickle_data from "ShowPickle" LIMIT 1')  #
        mypickle = cursor.fetchone()[0]

        Cartoondict = pickle.loads(mypickle)
        return Cartoondict
    except:
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
    cartoon_list_page = open('CartoonList.html').read()

    def render_Cartoon_template(node):
        node.Cartoon_Attribute.repeat(render_cartoonAtr, Cartoondict)

    def render_cartoonAtr(node, cartoonsection):
        node.Cartoon_Title_Attribute.text = Cartoondict[cartoonsection].showname
        node.Cartoon_Link_Attribute.atts['href'] = Cartoondict[cartoonsection].showlink

    cartoon_list_template = Template(cartoon_list_page)
    return cartoon_list_template.render(render_Cartoon_template)


@app.route('/anime_list', methods=['GET',])
def anime_list():
    load_database()
    anime_list_page = open('AnimeList.html').read()

    def render_anime_template(node):
        node.Anime_Attribute.repeat(render_animeAtr, Animedict)

    def render_animeAtr(node, animesection):
        node.Anime_Title_Attribute.text=Animedict[animesection].showname
        node.Anime_Link_Attribute.text=Animedict[animesection].showlink

    anime_list_template = Template(anime_list_page)
    return anime_list_template.render(render_anime_template)


@app.route('/<path:path>')
def send_js(path):
    return send_from_directory('', path)


@app.route('/cartoon/<id>')
def get_cartoon():
    pass


@app.route('/anime/<id>')
def get_anime():
    pass


@app.route('/cartoon/<id>/delete')
def delete_cartoon():
    pass


@app.route('/anime/<id>/delete')
def delete_anime():
    pass


@app.route('/cartoon/<id>/update')
def update_cartoon():
    pass


@app.route('/anime/<id>/update')
def update_anime():
    pass


@app.route('/')
def home():
    this_folder = os.path.dirname(os.path.abspath(__file__))
    home_page = os.path.join(this_folder, 'Home.html')
    with open(home_page) as home:
        list_page = open(home_page).read()
        return list_page


@app.route('/cartoon/new', methods=['POST',])
def add_cartooon():
    # instantiate a new show object and populate it from request.form
    New_Cartoon = cartoon_show_object(
        showname=request.form['Cartoon_Title_Input'],
        showimage=request.form['Image_Input'],
        showlink=request.form['Cartoon_Link_Input']
    )

    Cartoondict[New_Cartoon.id] = New_Cartoon
    save_database()
    return redirect('/')


@app.route('/cartoon/new', methods=['GET',])
def get_add_cartooon_form():
    this_folder = os.path.dirname(os.path.abspath(__file__))
    add_cartoon_page = os.path.join(this_folder, 'Cartoon_Edit.html')
    return open(add_cartoon_page).read()


@app.route('/anime/new', methods=['POST',])
def add_anime():
    # instantiate a new show object and populate it from request.form
    New_Anime = anime_show_object(
        showname=request.form['Anime_Title_Input'],
        showimage=request.form['Image_Input'],
        showlink=request.form['Anime_Link_Input']
    )

    Animedict[New_Anime.id] = New_Anime
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
