from flask import Flask
import os

intyme = Flask(__name__)
intyme.config["SECRET_KEY"] = "23gd5s5g1s3f1s3df13sd1vf3c1v2x1vc3x51v"
intyme.config["IMAGE_UPLOADS"] = os.getcwd().replace("\\","/") + "/Intyme/static/uploads"

from Intyme import common_views
from Intyme import student_views
from Intyme import teacher_views
from Intyme import functions

