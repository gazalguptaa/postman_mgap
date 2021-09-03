import os
from flask import Flask

app = Flask(__name__, static_folder = "assets")
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True} 
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
env='dev'
if env=='dev':
    app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:02Nj$P@1@localhost/project'
    app.debug = True

else:
    app.config['SQLALCHEMY_DATABASE_URI']='postgres://lumkgmaezmycfk:f75928cf27f1195702281e4759711544b9f80d982de3440398ee39caaa631a48@ec2-34-232-212-164.compute-1.amazonaws.com:5432/dd0ddh8fneqtkf'
    app.debug = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


from routes import *
from models import *


db.create_all() 

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)