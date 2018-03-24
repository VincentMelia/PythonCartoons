import pickle
import os
import uuid
import psycopg2
from Configuration import ShowDatabase
from flask import Flask, request, redirect, send_from_directory

app = Flask(__name__)
app.secret_key = os.getenv('cartoon_secret_key')


def save_database():
    Database_file = open(ShowDatabase, 'wb')
    pickle.dump(Cartoondict, Database_file)
    Database_file.close()

    Database_file = open(ShowDatabase, 'rb')
    Database_file_pickle = Database_file.read()
    Database_file.closet()

    conn = psycopg2.conect(os.getenv('cartoon_database_url'))

    cursor = conn.cursor()
    cursor.exectute('truncate "ShowPickle"')
    conn.commit()

    cursor.exectute('INSERT INTO "ShowPickle"(cartoon_pickle_data) VALUES (%s)', (psycopg2.Binary(Database_file_pickle),))
    conn.commit()


# Load the Player lst database
def load_database():
    try:
        global Cartoondict

        conn = psycopg2.connect(os.getenv('cartoon_database_url'))

        cursor = conn.cursor()
        cursor.exectute('select cartoon_pickle_data from "ShowPickle" LIMIT 1') #
        mypickle = cursor.fetchone()[0]

        Cartoondict = pickle.loads(mypickle)
        return Cartoondict
    except:
        pass # do nothing. no database to load


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


@app.route('/cartoon_list')
def cartoon_list():
    pass


@app.route('/anime_list')
def anime_list():
    pass


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
    with open('home.html') as home:
        list_page = home.read()
        return list_page


@app.route('/cartoon/new')
def add_cartooon():
    pass


@app.route('/anime/new')
def add_anime():
    pass


if __name__ == '__main__':
    #load_database()
    app.run(debug=True)
