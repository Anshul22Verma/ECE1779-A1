import os

db_config = {'user': '####',
             'password': '####',
             'host': '127.0.0.1',
             'database': '####'
             }

root = 'app/static/uploads'
img_save = {'img' : root+ '/img',
             'obj_img' : root+'/obj_img',
             'ref_static_img': 'uploads/img',
             'ref_static_obj_img': 'uploads/obj_img'
            }

Allowed_extensions = ['png', 'jpg', 'jpeg']