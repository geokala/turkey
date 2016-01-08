#! /usr/bin/env python
from datetime import timedelta, datetime
import turkey
from turkey.db import db, User
from sqlalchemy.orm.exc import NoResultFound

if __name__ == '__main__':
    db.create_all()

    try:
        User.query.filter(User.name == "admin").one()
    except NoResultFound:
        user = User("admin", "admin@turkey.local", "admin")
        user.confirmed_at = datetime.now() - timedelta(days=2)
        user.is_admin = True
        db.session.add(user)
        db.session.commit()

    turkey.app.config["SECRET_KEY"] = ("I AM THE DEVELOPMENT SECRET KEY!"
                                       "DO NOT COMMIT ME TO PRODUCTION")
    turkey.app.config["DEBUG"] = True
    turkey.app.run()
