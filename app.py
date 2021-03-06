from flask import Flask, render_template, request, json, session, redirect, jsonify
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import re


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

app.secret_key = 'why would I tell you my secret key?'
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'ballusers'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)




@app.route("/")
def main():
    if session.get('user'):
        conn = mysql.connect()
        cursor = conn.cursor()
        follows = get_follows(cursor,session.get('user'))

        names = get_names(cursor,follows)
        

        return render_template('userHome.html', follows=names)
    else:
        return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/signUp',methods=['POST'])
def signUp():
    # read the posted values
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']

    # validate the received values
    if _name and _email and _password:
        conn = mysql.connect()
        cursor = conn.cursor()
        
        _hashed_password = generate_password_hash(_password)
        cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
        
        data = cursor.fetchall()

        if len(data) is 0:
            conn.commit()
            return json.dumps({'message':'User created successfully'})
        else:
            return json.dumps({'error':str(data[0])})

    else:
        return json.dumps({'html': '<span>Missing field</span>'})


@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')


@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        # connect to mysql
 
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()
 
 
        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][0]
                return redirect('/')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
 
 
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()


@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')




@app.route('/getPlayers',methods=['POST'])
def getPlayers():
    term = request.values['search_keyword']
    print term
    
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT * FROM players WHERE player_name LIKE ' + '"%' + str(term) + '%"' + ' LIMIT 10;'
    cursor.execute(query)
    data = cursor.fetchall()
    return jsonify(data)


@app.route('/followPlayer',methods=['POST'])
def followPlayers():
    if session.get('user'):
        player = str(request.values['player'])
        player_id = re.findall('/player/(.+)', player)[0] 

        user = session.get('user')
        print user

        conn = mysql.connect()
        cursor = conn.cursor()
        query = 'INSERT INTO follows (user_id, player_id) VALUES (' + str(user) + ', ' + str(player_id) + ');'
        print query

        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        return player_id



@app.route('/player/<int:player_id>')
def player(player_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT * FROM players WHERE player_id =' + str(player_id) + ';'
    cursor.execute(query)
    data = cursor.fetchall()
    name = data[0][1]
    return render_template('player.html', name=name)


def get_follows(cursor,user):
    #this returns the list of players a user is following, in id format
    query = 'SELECT player_id FROM follows WHERE user_id = ' + str(user) + ';'
    cursor.execute(query)
    data = cursor.fetchall()

    follows = []
    for datum in data:
        follows.append(datum[0])

    return follows


def get_names(cursor,player_ids):
    #this takes in a list of player_ids and returns a list of their names
    query = 'SELECT player_name from players WHERE player_id IN ' + str(player_ids).replace('[','(').replace(']',')') + ';'
    cursor.execute(query)
    stuff = cursor.fetchall()

    names = []
    for s in stuff:
        names.append(str(s[0]))
    return names



if __name__ == "__main__":
    app.run()


