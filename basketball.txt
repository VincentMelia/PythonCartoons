from Configuration import BasketballPlayerDatabase, Root_URL

from BasketballPlayer import BasketballPlayer
import pickle
from flask import Flask, request, render_template, redirect, send_from_directory
from htmltemplate import Template
from PIL import Image
import base64

import os
import uuid
import psycopg2


app = Flask(__name__)
app.secret_key = os.getenv('basketball_secret_key')

Playerdict = {}

# Save player list to Database
def save_database():
    Database_file = open(BasketballPlayerDatabase, 'wb')
    pickle.dump(Playerdict, Database_file)
    Database_file.close()

    Database_file = open(BasketballPlayerDatabase, 'rb')
    database_file_pickle = Database_file.read()
    Database_file.close()

    #conn = psycopg2.connect(database=Database, user=Database_user, password=Database_password, host=Database_host,
    #                        port=Database_port)
    conn = psycopg2.connect(os.getenv('basketball_database_url'))

    cursor = conn.cursor()
    cursor.execute('truncate "BasketballPickle"')
    conn.commit()

    cursor.execute('INSERT INTO "BasketballPickle"(pickle_data) VALUES (%s)', (psycopg2.Binary(database_file_pickle),))
    conn.commit()


# Load the Player list database
def load_database():
    try:
        global Playerdict

        #conn = psycopg2.connect(database=Database, user=Database_user, password=Database_password, host=Database_host,
        #                        port=Database_port)
        conn = psycopg2.connect(os.getenv('basketball_database_url'))

        cursor = conn.cursor()
        cursor.execute('select pickle_data from "BasketballPickle" LIMIT 1')  #
        mypickle = cursor.fetchone()[0]

        Playerdict = pickle.loads(mypickle)
        return Playerdict
    except:
        pass  # do nothing. no database to load


def setup_database():
    #conn = psycopg2.connect(database=Database, user=Database_user, password=Database_password, host=Database_host,
    #                        port=Database_port)
    conn = psycopg2.connect(os.getenv('basketball_database_url'))

    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE public."BasketballPickle"
        (
            pickle_data bytea
        )
        WITH (
            OIDS=FALSE
        );
    ''')
    conn.commit()


@app.route('/initdb')
def init_database():
    setup_database()
    return redirect('/player_list')


@app.route('/player', methods=['GET', 'POST'])
def new_player():
    load_database()
    if request.method == 'POST':
        file = request.files['Image_Input']

        if file.filename != '':
            img = Image.open(file)
            img.thumbnail((500, 555))
            img.save(file.filename)
            img.close()
            img = open(file.filename, 'rb')

            New_Basketball_Player = BasketballPlayer(name=request.form['Name_Input'],
                                                 age=request.form['Age_Input'],
                                                 height=request.form['Height_Input'],
                                                 weight=request.form['Weight_Input'],
                                                 team=request.form['Team_Input'],
                                                 number=request.form['Number_Input'],
                                                 position=request.form['Position_Input'],
                                                 points_per_game=request.form['Points_Per_Game_Input'],
                                                 assist_per_game=request.form['Assist_Per_Game_Input'],
                                                 blocks_per_game=request.form['Blocks_Per_Game_Input'],
                                                 rebounds_per_game=request.form['Rebounds_Per_Game_Input'],
                                                 steals_per_game=request.form['Steals_Per_Game_Input'],
                                                 fouls_per_game=request.form['Fouls_Per_Game_Input'],
                                                 freethrows_per_game=request.form['Freethrows_Per_Game_Input'],
                                                 championships_won=request.form['Championships_Won_Input'],
                                                 image=img.read(),
                                                 id=uuid.uuid4())
            img.close()
            os.remove(file.filename)
        else:
            New_Basketball_Player = BasketballPlayer(name=request.form['Name_Input'],
                                                 age=request.form['Age_Input'],
                                                 height=request.form['Height_Input'],
                                                 weight=request.form['Weight_Input'],
                                                 team=request.form['Team_Input'],
                                                 number=request.form['Number_Input'],
                                                 position=request.form['Position_Input'],
                                                 points_per_game=request.form['Points_Per_Game_Input'],
                                                 assist_per_game=request.form['Assist_Per_Game_Input'],
                                                 blocks_per_game=request.form['Blocks_Per_Game_Input'],
                                                 rebounds_per_game=request.form['Rebounds_Per_Game_Input'],
                                                 steals_per_game=request.form['Steals_Per_Game_Input'],
                                                 fouls_per_game=request.form['Fouls_Per_Game_Input'],
                                                 freethrows_per_game=request.form['Freethrows_Per_Game_Input'],
                                                 championships_won=request.form['Championships_Won_Input'],
                                                 id=uuid.uuid4())

        Playerdict[str(New_Basketball_Player.id)] = New_Basketball_Player

        save_database()

        return redirect('/player_list')

    if request.method == 'GET':
        with open('PlayerEditor.html') as player_list_file:
            player_editor = open('PlayerEditor.html').read()

        def render_PlayerAtr(node, playerobject):
            node.ActionPathAtr.atts['action'] = '/player'  # + str(playerobject.id)
            node.ActionPathAtr.NameAtr.atts['value'] = ''
            node.ActionPathAtr.TeamAtr.atts['value'] = ''
            node.ActionPathAtr.AgeAtr.atts['value'] = ''
            node.ActionPathAtr.JerseyAtr.atts['value'] = ''
            node.ActionPathAtr.PositionAtr.atts['value'] = ''
            node.ActionPathAtr.HeightAtr.atts['value'] = ''
            node.ActionPathAtr.WeightAtr.atts['value'] = ''
            node.ActionPathAtr.ChampionshipsAtr.atts['value'] = ''
            node.ActionPathAtr.PointsAtr.atts['value'] = ''
            node.ActionPathAtr.StealsAtr.atts['value'] = ''
            node.ActionPathAtr.BlocksAtr.atts['value'] = ''
            node.ActionPathAtr.ReboundsAtr.atts['value'] = ''
            node.ActionPathAtr.FoulsAtr.atts['value'] = ''
            node.ActionPathAtr.AssistAtr.atts['value'] = ''
            node.ActionPathAtr.FreeThrowAtr.atts['value'] = ''
            # node.ActionPathAtr.IdAtr.atts['value']  = playerobject.id

        player_editor_template = Template(player_editor)
        # return player_editor_template.render(render_PlayerAtr)
    return player_editor_template.render(render_PlayerAtr, [])


@app.route('/player/<id>', methods=['GET', 'POST'])
def get_player(id):
    global Playerdict
    load_database()
    if request.method == 'GET':
        playerobjectfromdictionary = Playerdict[id]

        if playerobjectfromdictionary.image is not None:
            data64 = u'data:%s;base64,%s' % (
                'image/jpg', base64.encodebytes(playerobjectfromdictionary.image).decode('utf8'))
        else:
            data64 = None
        # return render_template('test.html', form=f, img=data64)

        with open('PlayerEditor.html') as player_list_file:
            list_page = open('PlayerEditor.html').read()

        def render_PlayerAtr(node, playerobject):
            node.ActionPathAtr.atts['action'] = '/player/' + str(playerobject.id)
            node.ActionPathAtr.NameAtr.atts['value'] = playerobject.name
            node.ActionPathAtr.TeamAtr.atts['value'] = playerobject.team
            node.ActionPathAtr.AgeAtr.atts['value'] = playerobject.age
            node.ActionPathAtr.JerseyAtr.atts['value'] = playerobject.number
            node.ActionPathAtr.PositionAtr.atts['value'] = playerobject.position
            node.ActionPathAtr.HeightAtr.atts['value'] = playerobject.height
            node.ActionPathAtr.WeightAtr.atts['value'] = playerobject.weight
            node.ActionPathAtr.ChampionshipsAtr.atts['value'] = playerobject.championships_won
            node.ActionPathAtr.PointsAtr.atts['value'] = playerobject.points_per_game
            node.ActionPathAtr.StealsAtr.atts['value'] = playerobject.steals_per_game
            node.ActionPathAtr.BlocksAtr.atts['value'] = playerobject.blocks_per_game
            node.ActionPathAtr.ReboundsAtr.atts['value'] = playerobject.rebounds_per_game
            node.ActionPathAtr.FoulsAtr.atts['value'] = playerobject.fouls_per_game
            node.ActionPathAtr.AssistAtr.atts['value'] = playerobject.assist_per_game
            node.ActionPathAtr.FreeThrowAtr.atts['value'] = playerobject.freethrows_per_game
            node.ActionPathAtr.DisplayImgAtr.atts['src'] = data64

        player_editor_template = Template(list_page)
        return player_editor_template.render(render_PlayerAtr, playerobjectfromdictionary)

    if request.method == 'POST':
        updated_basketball_player = Playerdict[id]

        file = request.files['Image_Input']

        if file.filename != '':
            img = Image.open(file)
            img.thumbnail((500, 555))
            img.save(file.filename)
            img.close()
            img = open(file.filename, 'rb')
            read_image = img.read()
            img.close()
        updated_basketball_player.name = request.form['Name_Input']
        updated_basketball_player.age = request.form['Age_Input']
        updated_basketball_player.height = request.form['Height_Input']
        updated_basketball_player.weight = request.form['Weight_Input']
        updated_basketball_player.team = request.form['Team_Input']
        updated_basketball_player.number = request.form['Number_Input']
        updated_basketball_player.position = request.form['Position_Input']
        updated_basketball_player.points_per_game = request.form['Points_Per_Game_Input']
        updated_basketball_player.assist_per_game = request.form['Assist_Per_Game_Input']
        updated_basketball_player.blocks_per_game = request.form['Blocks_Per_Game_Input']
        updated_basketball_player.rebounds_per_game = request.form['Rebounds_Per_Game_Input']
        updated_basketball_player.fouls_per_game = request.form['Fouls_Per_Game_Input']
        updated_basketball_player.steals_per_game = request.form['Steals_Per_Game_Input']
        updated_basketball_player.freethrows_per_game = request.form['Freethrows_Per_Game_Input']
        updated_basketball_player.championships_won = request.form['Championships_Won_Input']
        updated_basketball_player.image = read_image

    Playerdict[id] = updated_basketball_player
    save_database()
    return redirect('/player_list')


@app.route('/player/<id>/delete')
def delete_player(id):
    global Playerdict
    load_database()
    if request.method == 'GET':
        del Playerdict[id]
        save_database()
        return redirect('/player_list')


@app.route('/')
def main_page():
    return redirect('/player_list')


@app.route('/player_list')
def player_list():
    load_database()

    with open('PlayerList.html') as player_list_file:
        list_page = open('PlayerList.html').read()

    def render_template2(node):
        node.PlayerAtr.repeat(render_PlayerAtr, Playerdict)

    def render_PlayerAtr(node, playersection):
        node.NameAtr.text = Playerdict[playersection].name
        node.TeamAtr.text = Playerdict[playersection].team
        node.AgeAtr.text = Playerdict[playersection].age
        node.JerseyAtr.text = Playerdict[playersection].number
        node.PositionAtr.text = Playerdict[playersection].position
        node.HeightAtr.text = Playerdict[playersection].height
        node.WeightAtr.text = Playerdict[playersection].weight
        node.ChampionshipsAtr.text = Playerdict[playersection].championships_won
        node.PointsAtr.text = Playerdict[playersection].points_per_game
        node.StealsAtr.text = Playerdict[playersection].steals_per_game
        node.BlocksAtr.text = Playerdict[playersection].blocks_per_game
        node.ReboundsAtr.text = Playerdict[playersection].rebounds_per_game
        node.FoulsAtr.text = Playerdict[playersection].fouls_per_game
        node.AssistAtr.text = Playerdict[playersection].assist_per_game
        node.FreeThrowAtr.text = Playerdict[playersection].freethrows_per_game
        node.IdAtr.text = Playerdict[playersection].id
        node.Delete.atts['href'] = '/player/' + str(Playerdict[playersection].id) + '/delete'
        node.Edit.atts['href'] = '/player/' + str(Playerdict[playersection].id)

    player_list_template = Template(list_page)
    return player_list_template.render(render_template2)


@app.route('/<path:path>')
def send_js(path):
    return send_from_directory('', path)


'''
if __name__ == '__main__':
    from cherrypy import wsgiserver
    d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
    server = wsgiserver.CherryPyWSGIServer(('192.168.1.235', 5000), d)
    try:
        load_database()
        server.start()
    except KeyboardInterrupt:
        server.stop()
'''

if __name__ == '__main__':
    load_database()
    app.run(debug=True)
