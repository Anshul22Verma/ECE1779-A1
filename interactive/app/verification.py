from app.config import Allowed_extensions
from app.Hashing_n_Checking import verify_password
import mysql.connector


def Unique_Name(cursor, ID, name, ext, i = 0):
    query = '''SELECT i.Imgname
                    FROM userinfo u, user_has_imgs ui, imgs i
                    WHERE ui.userinfo_UserID = %s AND i.Imgname = %s AND ui.imgs_ImgID = i.ImgID'''
    cursor.execute(query, (ID, (name+'.'+ext)))
    already_exist = cursor.fetchone()
    while (already_exist != None):
        i = i+1
        new_name = name+str(i)
        cursor.execute(query, (ID, (new_name + '.' + ext)))
        already_exist = cursor.fetchone()
        if(already_exist == None):
            name = new_name
    else:
        return name

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in Allowed_extensions

def User_Authentication(cursor, username, password):
    query = "SELECT * FROM userinfo WHERE Username = %s"
    cursor.execute(query, (username,))
    account = cursor.fetchone()

    if account is not None:
        ID = account[0]
        hashedpass = account[2]
        if (verify_password(hashedpass, str(password)) == True):
            msg = 'N/A'
            return True, msg, ID
        else:
            msg = 'Incorrect Password !'
            return False, msg, ID
    else:
        msg = 'Username does not exist !'
        return False, msg, 0