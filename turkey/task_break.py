from flask.ext.login import login_required, current_user
from turkey.models import TaskBreak, Task
from sqlalchemy.orm.exc import NoResultFound
from flask import request, redirect, url_for, flash
from wtforms import (
    Form,
    TextField,
    validators,
    SelectField,
    TextAreaField,
    DateField,
)
from turkey.utils import render_turkey
import datetime
from urllib import parse


class TaskBreakForm(Form):
    task_comment = TextAreaField(
        'Comment',
    )


def try_to_take_task_break(task_id, form, date=None):
    if date is not None:
        break_date = datetime.datetime.strptime(
            date,
            '%Y %b %d',
        )
        just_before_midnight = datetime.datetime.max.time()
        break_time = datetime.datetime.combine(
            break_date,
            just_before_midnight,
        )
    else:
        break_time = datetime.datetime.now()

    task_break = TaskBreak.create(
        comment=form.task_comment.data,
        associated_task_id=task_id,
        break_time=break_time,
        owner_id=current_user.id,
    )

    if task_break is None:
        # TODO: better output from this
        flash(
            'Could not take break from task!',
            'danger',
        )
        return redirect(request.referrer)
    else:
        # TODO: improve this message
        flash(
            'Taking a break...',
            'success',
        )
        return redirect(url_for('home'))


@login_required
def task_break_view(task_id, task_date):
    form = TaskBreakForm(request.form)

    try:
        task = Task.query.filter(
            Task.id == task_id,
            Task.owner_id == current_user.id,
        ).one()
    except NoResultFound:
        # This is not an existing task this user owns
        flash(
            'Could not find task {id}.'.format(id=task_id),
            'danger',
        )
        return redirect(url_for('home'))

    date = parse.unquote_plus(task_date)
    if request.method == 'POST' and form.validate():
        return try_to_take_task_break(
            task_id=task_id,
            form=form,
            date=date,
        )
    else:
        return render_turkey(
            "task_break.html",
            form=form,
            task=task,
            task_date=date,
        )
