# Defining the API extensions
from flask import g, session, request, flash, send_from_directory, jsonify, Response
from app import webapp
import os, re, io
from werkzeug.utils import secure_filename
from app.verification import Unique_Name, allowed_file, User_Authentication
from app.objdetect import objdetect
from PIL import Image
from app.Hashing_n_Checking import hash_password
from app.main import get_db

from app.config import db_config, img_save

#api extension for user registration
@webapp.route('/api/register/', methods=['POST'])
def add_user():
    username = request.args.get('username')
    password = request.args.get('password')
    # Because only numeric usernames and passwords are allowed
    password = str(password)
    username = str(username)

    cnx = get_db()
    cursor = cnx.cursor(buffered=True)
    query = "SELECT UserID FROM userinfo WHERE Username = %s"
    cursor.execute(query, (username,))
    account = cursor.fetchone()
    if account is not None:
        msg = "Username already exists"
        code = 406
    else:
        if username == '' or password == '':
            msg = 'Not a valid Username or Password'
            code = 406
        elif (len(username) > 100):
            msg = 'username > 100'
            code = 406
        else:
            hashedpass = hash_password(password)
            query = 'INSERT INTO userinfo (UserID, Username, HashedPassword) VALUES (NULL, %s, %s)'
            cursor.execute(query, (username, hashedpass))
            cnx.commit()
            msg = 'Successfuly created new user.'
            code = 202
    return jsonify({'msg' : msg}), code

#api extension for uploading image
@webapp.route('/api/upload', methods=['GET','POST'])
def add_image():
    username = request.form.get('username')
    password = request.form.get('password')

    # Because we allow only numeric and character based passwords and username
    username =str(username)
    password = str(password)
    cnx = get_db()
    cursor = cnx.cursor(buffered=True)
    Authenticate, msg, ID = User_Authentication(cursor, username, password)
    if Authenticate:
        if 'file' not in request.files:
            return jsonify({'msg': 'No file found', 'state':406, 'status':'None'}), 200
        else:
            pic = request.files['file']
            pic.seek(0, os.SEEK_END)
            size = pic.tell()
            if size > (100 * (1e6)):
                return jsonify({'msg': 'File too big', 'state':401, 'status':'Rejected'}), 401
            elif pic.filename == "":
                return jsonify({'msg': 'Invalid Filename', 'state':406, 'status':'Rejected'}), 406
            elif pic and allowed_file(pic.filename):
                filename = secure_filename(pic.filename)
                #Logged in user can use other users credentials but uploaded pic will only be accessible to the logged in user ID

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
                    return jsonify({'i': 201, 'mdg': 'Accepted'}), 200
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
                    return jsonify({'i':200, 'mdg':'Accepted'}), 200
            else:
                return jsonify({'msg': 'Incorrect file format', 'state':406, 'status':'Rejected'}), 406
    return jsonify({'msg': 'Cant Login', 'state':401, 'status':'Rejected'}), 401