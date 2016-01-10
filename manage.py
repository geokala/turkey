#! /usr/bin/env python
import os
import sys
import json
import random
import string

from flask.ext.script import Manager, Server
from turkey import app

if os.path.isfile('turkey.conf'):
    with open('turkey.conf') as conf_handle:
        conf_data = conf_handle.read()
    config = json.loads(conf_data)
else:
    random_key = ''.join([random.choice(string.ascii_letters)
                         for char in range(80)])
    config = {
        'SECRET_KEY': random_key,
        'DEBUG': False,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    }
app.config.update(config)

manager = Manager(app)

manager.add_command("runserver", Server(
    use_debugger=False,
    use_reloader=True,
    host='0.0.0.0')
)

if __name__ == "__main__":
    manager.run()
