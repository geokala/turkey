import datetime
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask_login import UserMixin
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
    owner_id = db.Column(db.Integer(),
                         db.ForeignKey('users.id'),
                         nullable=False)
    comment = db.Column(db.String(1024))
    completed_time = db.Column(db.DateTime())
    completed_later = db.Column(db.Boolean(),
                                default=False)

    def __init__(self, comment, completed_time, associated_task_id, owner_id,
                 completed_later):
        self.comment = comment
        self.completed_time = completed_time
        self.associated_task_id = associated_task_id
        self.owner_id = owner_id
        self.completed_later = completed_later

    @staticmethod
    def create(comment, completed_time, owner_id, associated_task_id=None,
               completed_later=False,):
        if task_not_completable(
            associated_task_id,
            date=completed_time,
        ):
            # Trying to complete a archived/completed/on break task
            completed_task = None
        else:
            try:
                completed_task = CompletedTask(
                    comment,
                    completed_time,
                    associated_task_id,
                    owner_id,
                    completed_later,
                )
                db.session.add(completed_task)
                db.session.commit()
            except IntegrityError:
                # Trying to complete a task that doesn't exist
                completed_task = None
        return completed_task

    @staticmethod
    def was_completed_on_date(associated_task_id, date):
        associated_task_id = int(associated_task_id)
        completed_tasks = CompletedTask.get_completed(date=date)
        return associated_task_id in completed_tasks

    @staticmethod
    def get_completed(date):
        midnight = datetime.datetime.min.time()
        date = datetime.datetime.combine(date, midnight)
        next_date = date + datetime.timedelta(days=1)
        completed_tasks = CompletedTask.query.filter(
            CompletedTask.completed_time > date,
            CompletedTask.completed_time < next_date,
        ).all()
        completed_tasks = [
            item.associated_task_id for item in completed_tasks
        ]
        return completed_tasks


def task_not_completable(task_id, date):
    if CompletedTask.was_completed_on_date(
        associated_task_id=task_id,
        date=date,
    ):
        # Already completed
        result = True
    elif TaskBreak.took_break_on_date(
        associated_task_id=task_id,
        date=date,
    ):
        # On break
        result = True
    elif Task.finished(
        task_id=task_id,
    ):
        # Archived
        result = True
    else:
        result = False
    return result


class TaskBreak(db.Model):
    __tablename__ = 'task_breaks'

    id = db.Column(db.Integer(), primary_key=True)
    associated_task_id = db.Column(db.Integer(),
                                   db.ForeignKey('tasks.id'),
                                   nullable=False)
    owner_id = db.Column(db.Integer(),
                         db.ForeignKey('users.id'),
                         nullable=False)
    comment = db.Column(db.String(1024))
    break_time = db.Column(db.DateTime())

    def __init__(self, comment, break_time, associated_task_id, owner_id):
        self.comment = comment
        self.break_time = break_time
        self.associated_task_id = associated_task_id
        self.owner_id = owner_id

    @staticmethod
    def create(comment, break_time, owner_id, associated_task_id=None):
        if task_not_completable(
            associated_task_id,
            date=break_time,
        ):
            # Trying to complete a archived/completed/on break task
            task_break = None
        else:
            try:
                task_break = TaskBreak(
                    comment,
                    break_time,
                    associated_task_id,
                    owner_id,
                )
                db.session.add(task_break)
                db.session.commit()
            except IntegrityError:
                # Trying to complete a task that doesn't exist
                task_break = None
        return task_break

    @staticmethod
    def took_break_on_date(associated_task_id, date):
        associated_task_id = int(associated_task_id)
        task_breaks = TaskBreak.get_breaks(date=date)
        return associated_task_id in task_breaks

    @staticmethod
    def get_breaks(date):
        midnight = datetime.datetime.min.time()
        date = datetime.datetime.combine(date, midnight)
        next_date = date + datetime.timedelta(days=1)
        task_breaks = TaskBreak.query.filter(
            TaskBreak.break_time > date,
            TaskBreak.break_time < next_date,
        ).all()
        task_breaks = [
            item.associated_task_id for item in task_breaks
        ]
        return task_breaks


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer(), primary_key=True)
    associated_goal_id = db.Column(db.Integer(),
                                   db.ForeignKey('goals.id'))
    owner_id = db.Column(db.Integer(),
                         db.ForeignKey('users.id'),
                         nullable=False)
    name = db.Column(db.String(255))
    creation_time = db.Column(db.DateTime())
    finish_time = db.Column(db.DateTime())

    def __init__(self, name, owner_id, associated_goal_id=None,
                 creation_time=None, finish_time=None):
        self.name = name
        self.associated_goal_id = associated_goal_id
        self.owner_id = owner_id
        self.creation_time = creation_time
        self.finish_time = finish_time

    @staticmethod
    def create(name, owner_id, associated_goal_id=None, creation_time=None,
               finish_time=None):
        try:
            Task.query.filter(
                Task.name == name,
                Task.associated_goal_id == associated_goal_id,
                Task.owner_id == owner_id,
            ).one()
        except NoResultFound:
            if creation_time == None:
                creation_time = datetime.datetime.now()
            task = Task(name, owner_id, associated_goal_id, creation_time)
            db.session.add(task)
            db.session.commit()
            return task

    def finish(self):
        self.finish_time = datetime.datetime.now()
        db.session.commit()
        return self.finish_time

    @staticmethod
    def finished(task_id):
        task = Task.query.filter(Task.id==task_id).one()
        return task.finish_time is not None


class Goal(db.Model):
    __tablename__ = 'goals'

    id = db.Column(db.Integer(), primary_key=True)
    parent_goal_id = db.Column(db.Integer(),
                               db.ForeignKey('goals.id'))
    owner_id = db.Column(db.Integer(),
                         db.ForeignKey('users.id'),
                         nullable=False)
    name = db.Column(db.String(255))

    def __init__(self, name, owner_id, parent_goal_id=None):
        self.name = name
        self.parent_goal_id = parent_goal_id
        self.owner_id = owner_id

    @staticmethod
    def create(name, owner_id, parent_goal_id=None):
        try:
            Goal.query.filter(
                Goal.name == name,
                Goal.parent_goal_id == parent_goal_id,
                Goal.owner_id == owner_id,
            ).one()
        except NoResultFound:
            goal = Goal(name, owner_id, parent_goal_id)
            db.session.add(goal)
            db.session.commit()
            return goal


class SiteAdmin(db.Model):
    __tablename__ = "site_administration"

    id = db.Column(db.Integer, primary_key=True)
    allow_user_registrations = db.Column(db.Boolean())

    def __init__(self, allow_user_registrations=True):
        self.allow_user_registrations = allow_user_registrations

    @staticmethod
    def user_registration(allowed=None):
        try:
            site_administration = SiteAdmin.query.one()
            site_administration.allow_user_registrations = allowed
        except NoResultFound:
            site_administration = SiteAdmin(allow_user_registrations=allowed)
            db.session.add(site_administration)
        db.session.commit()


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
            User.query.filter(User.name == name).union(
                User.query.filter(User.email == email)
            ).one()
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
