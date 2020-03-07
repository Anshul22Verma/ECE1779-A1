from flask import render_template, url_for, g, session, request, redirect, flash, send_from_directory
from app import webapp
import mysql.connector
import os, re, io
from werkzeug.utils import secure_filename
from app.verification import Unique_Name, allowed_file, User_Authentication
from app.objdetect import objdetect
from PIL import Image
from app.Hashing_n_Checking import hash_password
from datetime import timedelta

from app.config import db_config, img_save

webapp.secret_key = '\x80\xa9s*\x12\xc7x\xa9d\x1f(\x03\xbeHJ:\x9f\xf0!\xb1a\xaa\x0f\xee'

#functions to connect to data-base
def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#login page with its route
@webapp.route('/',methods=['GET'])
@webapp.route('/Login', methods = ['POST', 'GET'])
def main():
    if (request.method == 'POST' and 'username' in request.form and 'password' in request.form):
        username = request.form.get('username', "")
        password = request.form.get('password', "")
        #Because we allow only numeric and character based passwords
        password = str(password)
        cnx = get_db()
        cursor = cnx.cursor(buffered=True)

        Authenticate, msg, ID = User_Authentication(cursor, username, password)
        if Authenticate:

            session['loggedin'] = True
            session['id'] = ID
            session['username'] = username
            flash('Login Successful', 'isa_info')
            session.permanent = True
            webapp.permanent_session_lifetime = timedelta(hours=24)
            return redirect(url_for('home', username = username))
        else:
            flash(msg, 'isa_err')
            return render_template('main.html', username=username)
    return render_template('main.html')

@webapp.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form.get('username', "")
        password = request.form.get('password', "")
        #Because only numeric usernames and passwords are allowed
        password = str(password)
        username = str(username)

        cnx = get_db()
        cursor = cnx.cursor(buffered=True)
        query = "SELECT UserID FROM userinfo WHERE Username = %s"
        cursor.execute(query, (username,))
        account = cursor.fetchone()
        if account is not None:
            flash("Username already exists if its your then please Login or use a different username.", 'isa_info')
            return render_template('register.html', username = username)
        else:
            if username == '' or password == '':
                flash('Please enter a valid Username and Password', 'isa_err')
                return redirect(url_for('register'))
            elif (len(username) > 100):
                    flash ('Maximum length of allowed username is 100', 'isa_err')
                    return redirect(url_for('register'))
            else:
                flash('Registeration Successful !', 'isa_info')
                hashedpass = hash_password(password)
                query = 'INSERT INTO userinfo (UserID, Username, HashedPassword) VALUES (NULL, %s, %s)'
                cursor.execute(query, (username, hashedpass))
                cnx.commit()
                return render_template('main.html', username=username)
    return render_template('register.html')

@webapp.route('/<username>/home', methods = ['POST', 'GET'])
def home(username):
    if 'loggedin' in session:
        cnx = get_db()
        cursor = cnx.cursor(buffered=True)
        query = '''SELECT i.Imgname, i.Imgloc, i.ObjImgloc
                    FROM userinfo u, user_has_imgs ui, imgs i 
                    WHERE u.Username = %s AND u.UserID = ui.userinfo_UserID AND ui.imgs_ImgID = i.ImgID'''
        cursor.execute(query, (username,))
        images = cursor.fetchall()
        return render_template("home.html", username=username, L=images)
    return redirect(url_for('main', username=username))

@webapp.route('/upload', methods = ['POST', 'GET'])
def upload():
    if 'loggedin' in session:
        username = session['username']
    else:
        username = ''
    #Just setting the username
    if (request.method == 'POST' and 'username' in request.form and 'password' in request.form):
        username = request.form.get('username', "")
        password = request.form.get('password', "")
        # Because we allow only numeric and character based passwords
        password = str(password)
        cnx = get_db()
        cursor = cnx.cursor(buffered=True)
        Authenticate, msg, ID = User_Authentication(cursor, username, password)
        if Authenticate:
            if request.method == 'POST':
                if 'file' not in request.files:
                    flash('No file found!', 'isa_err')
                    return render_template('upload.html', username = username)
                else:
                    pic = request.files['file']
                    pic.seek(0, os.SEEK_END)
                    size = pic.tell()
                    if size > (100 * (1e6)) or size == None:
                        flash('Can not accept the file', 'isa_err')
                    elif pic.filename == "":
                        flash('No selected file!', 'isa_err')
                        return render_template('upload.html', username=username)
                    elif pic and allowed_file(pic.filename):
                        filename = secure_filename(pic.filename)
                        #Logged in user can use other users credentials but uploaded pic will only be accessible to the logged in user ID
                        ID = session['id']

                        [name, ext] = filename.rsplit('.', 1)
                        name = str(ID) + name
                        # Generating a unique file name based on what is existing in the database
                        nxt_unq_name = Unique_Name(cursor, ID, name, ext)
                        nxt_unq_name = nxt_unq_name + '.' + ext

                        # saving the image
                        img_loc = os.path.join(img_save['img'], nxt_unq_name)
                        # Opening Image using Pillow
                        im = Image.open(pic)
                        im.save(img_loc)

                        # changing it to the reference location to static
                        img_loc = img_save['ref_static_img'] + '/' + nxt_unq_name
                        img_arr = Image.open(pic.stream)
                        # img_arr.save(img_loc)
                        bytes_img, h, w, msg = objdetect(img_arr, ext)
                        if msg == 'Failed to do object detection':
                            flash('Failed to do object detection', 'isa_err')
                            return render_template('upload.html', username = username)
                        else:
                            detected_img = Image.open(io.BytesIO(bytes_img))

                            detected_img.save(os.path.join(img_save['obj_img'], ('obj_' + nxt_unq_name)))
                            obj_loc = img_save['ref_static_obj_img'] + '/obj_' + nxt_unq_name

                            query = '''INSERT into imgs (Imgname, Imgloc, ObjImgloc)
                                                        VALUES(%s, %s, %s)'''
                            cursor.execute(query, (nxt_unq_name, img_loc, obj_loc))
                            # Can use last insert ID because ImgID is auto-increment type ID in imgs table
                            query = '''INSERT into user_has_imgs (userinfo_UserID, imgs_ImgID)
                                                                        VALUES(%s, LAST_INSERT_ID())'''
                            cursor.execute(query, (ID,))
                            cnx.commit()
                            flash('Image Uploaded', 'isa_info')
                            query = '''SELECT i.Imgname, i.Imgloc, i.ObjImgloc
                                        FROM userinfo u, user_has_imgs ui, imgs i 
                                        WHERE u.Username = %s AND u.UserID = ui.userinfo_UserID AND ui.imgs_ImgID = i.ImgID'''
                            cursor.execute(query, (username,))
                            images = cursor.fetchall()
                            return render_template('home.html', username=username, L=images)
                    else:
                        flash('Only enter .png and .jpeg type files!', 'isa_err')
                        return render_template('upload.html', username = username)
            return render_template('upload.html', username=username)
        else:
            flash(msg, 'isa_err')
            return render_template('upload.html', username=username)
    return render_template("upload.html", username=username)

@webapp.route('/home/logout', methods = ['POST', 'GET'])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('Logged Out!', 'isa_info')
    return redirect(url_for('main'))
