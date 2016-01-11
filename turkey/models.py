import datetime
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask.ext.login import UserMixin
import hashlib
from random import choice
from string import ascii_letters, digits
import turkey


db = turkey.db


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class CompletedTask(db.Model):
    __tablename__ = 'completed_tasks'

    id = db.Column(db.Integer(), primary_key=True)
    associated_task_id = db.Column(db.Integer(),
                                   db.ForeignKey('tasks.id'),
                                   nullable=False)
    comment = db.Column(db.String(1024))
    completed_time = db.Column(db.DateTime())

    def __init__(self, comment, completed_time, associated_task_id):
        self.comment = comment
        self.completed_time = completed_time
        self.associated_task_id = associated_task_id

    @staticmethod
    def create(comment, completed_time, associated_task_id=None):
        if CompletedTask.was_completed_today(
            associated_task_id,
        ):
            # Trying to complete a completed (today) task
            completed_task = None
        else:
            try:
                completed_task = CompletedTask(
                    comment,
                    completed_time,
                    associated_task_id,
                )
                db.session.add(completed_task)
                db.session.commit()
            except IntegrityError:
                # Trying to complete a task that doesn't exist
                completed_task = None
        return completed_task

    @staticmethod
    def was_completed_today(associated_task_id):
        associated_task_id = int(associated_task_id)
        completed_tasks = CompletedTask.get_completed_today()
        return associated_task_id in completed_tasks

    @staticmethod
    def get_completed_today():
        current_day = datetime.date.today()
        midnight = datetime.datetime.min.time()
        current_day = datetime.datetime.combine(current_day, midnight)
        completed_tasks = CompletedTask.query.filter(
            CompletedTask.completed_time > current_day,
        ).all()
        completed_tasks = [
            item.associated_task_id for item in completed_tasks
        ]
        return completed_tasks


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer(), primary_key=True)
    associated_goal_id = db.Column(db.Integer(),
                                   db.ForeignKey('goals.id'))
    name = db.Column(db.String(255))

    def __init__(self, name, associated_goal_id=None):
        self.name = name
        self.associated_goal_id = associated_goal_id

    @staticmethod
    def create(name, associated_goal_id=None):
        try:
            Task.query.filter(
                Task.name == name,
                Task.associated_goal_id == associated_goal_id,
            ).one()
        except NoResultFound:
            task = Task(name, associated_goal_id)
            db.session.add(task)
            db.session.commit()
            return task


class Goal(db.Model):
    __tablename__ = 'goals'

    id = db.Column(db.Integer(), primary_key=True)
    parent_goal_id = db.Column(db.Integer(),
                               db.ForeignKey('goals.id'))
    name = db.Column(db.String(255))

    def __init__(self, name, parent_goal_id=None):
        self.name = name
        self.parent_goal_id = parent_goal_id

    @staticmethod
    def create(name, parent_goal_id=None):
        try:
            Goal.query.filter(
                Goal.name == name,
                Goal.parent_goal_id == parent_goal_id,
            ).one()
        except NoResultFound:
            goal = Goal(name, parent_goal_id)
            db.session.add(goal)
            db.session.commit()
            return goal


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(255), unique=True)
    _password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())
    created_on = db.Column(db.DateTime())
    confirmation_code = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean(), default=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
        self.active = True
        self.confirmed_at = None
        self.created_on = datetime.datetime.now()
        self.confirmation_code = "".join(choice(ascii_letters + digits)
                                         for _ in range(32))

    @property
    def password(self):
        return self._password

    @property
    def salt(self):
        return hashlib.md5(bytes(self.name, 'utf8')).digest()

    def hash_password(self, password):
        return hashlib.pbkdf2_hmac(
            hash_name='sha256',
            password=bytes(password, 'utf8'),
            salt=self.salt,
            iterations=100000,
        )

    @password.setter
    def password(self, password):
        self._password = self.hash_password(password)

    def is_active(self):
        # TODO: Use self.confirmed_at <= datetime.datetime.now() again?
        # After we have a confirmation method.
        return self.active

    def validate_password(self, password):
        return self.password == self.hash_password(password)

    @staticmethod
    def create(name, email, password):
        try:
            User.query.filter(User.name == name).one()
            return None
        except NoResultFound:
            user = User(name, email, password)
            db.session.add(user)
            db.session.commit()
            return user

    def promote_admin(self):
        if not self.is_admin:
            self.is_admin = True
            db.session.commit()
        return self

    def demote_admin(self):
        if self.is_admin:
            self.is_admin = False
            db.session.commit()
        return self
