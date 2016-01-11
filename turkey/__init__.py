import os
import json
import random
import string

from flask import Flask
from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.sqlalchemy import SQLAlchemy

if os.path.isfile('turkey.conf'):
    with open('turkey.conf') as conf_handle:
        conf_data = conf_handle.read()
    config = json.loads(conf_data)
else:
    random_key = ''.join([random.choice(string.ascii_letters)
                         for char in range(80)])
    sqlite_path = '{homedir}/.turkey.db'.format(
        homedir=os.path.expanduser('~'),
    )
    config = {
        'SECRET_KEY': random_key,
        'DEBUG': False,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_DATABASE_URI': "sqlite:///{path}".format(
            path=sqlite_path,
        ),
    }

app = Flask(__name__)
app.config.update(config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.db = db

manager = Manager(app)
manager.add_command('db', MigrateCommand)

manager.add_command("runserver", Server(
    use_debugger=config['DEBUG'],
    use_reloader=True,
    host='0.0.0.0')
)

# Make sure we have all routes defined
from turkey import routes  # noqa
