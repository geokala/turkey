from flask.ext.login import login_required, current_user
from turkey.models import Task, CompletedTask
from sqlalchemy.orm.exc import NoResultFound
from flask import request, render_template, redirect, url_for, flash
from wtforms import (
    Form,
    TextField,
    validators,
    SelectField,
    TextAreaField,
    DateField,
)
from turkey.utils import int_or_null, get_goals, get_completed_tasks_history
import datetime
from urllib import parse


class CreateTaskForm(Form):
    task_name = TextField(
        'Task name',
        [
            validators.Length(max=255),
            validators.Required(),
        ],
    )
    associated_goal = SelectField(
        'Associated goal',
        coerce=int_or_null,
    )


class CompleteTaskForm(Form):
    task_comment = TextAreaField(
        'Comment',
    )


class CompleteOldTaskForm(Form):
    task_comment = TextAreaField(
        'Comment',
    )


def try_to_complete_task(task_id, form, date=None):
    if date is not None:
        completion_date = datetime.datetime.strptime(
            date,
            '%Y %b %d',
        )
        just_before_midnight = datetime.datetime.max.time()
        completion_time = datetime.datetime.combine(
            completion_date,
            just_before_midnight,
        )
        completed_later = True
    else:
        completion_time = datetime.datetime.now()
        completed_later = False

    completed_task = CompletedTask.create(
        comment=form.task_comment.data,
        associated_task_id=task_id,
        completed_time=completion_time,
        owner_id=current_user.id,
        completed_later=completed_later,
    )

    if completed_task is None:
        # TODO: better output from this
        flash(
            'Task could not be completed!',
            'danger',
        )
        return redirect(request.referrer)
    else:
        # TODO: improve this message
        flash(
            'Task completed.',
            'success',
        )
        return redirect(url_for('home'))



@login_required
def task_info_view(task_id):
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

    current_day = datetime.date.today()
    midnight = datetime.datetime.min.time()
    current_day = datetime.datetime.combine(current_day, midnight)

    creation_day = datetime.datetime.combine(task.creation_time, midnight)

    creation_history_delta = (current_day - creation_day).days

    task_history = get_completed_tasks_history(
        task_id=task_id,
        days=creation_history_delta,
    )
    task_name = task.name

    for task in task_history:
        task['date_quoted'] = parse.quote_plus(task['date'])

    days_ago = []
    while current_day >= creation_day:
        days_ago.append(current_day)
        current_day = current_day - datetime.timedelta(days=1)

    return render_template(
        'task_info.html',
        history=task_history,
        task_name=task_name,
    )


@login_required
def complete_old_task_view(task_id, task_date):
    form = CompleteOldTaskForm(request.form)

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
        return try_to_complete_task(
            task_id=task_id,
            form=form,
            date=date,
        )
    else:
        return render_template(
            "complete_old_task.html",
            form=form,
            task=task,
            task_date=date,
        )

@login_required
def complete_task_view(task_id):
    form = CompleteTaskForm(request.form)

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

    if request.method == 'POST' and form.validate():
        return try_to_complete_task(
            task_id=task_id,
            form=form,
        )
    else:
        return render_template("complete_task.html", form=form, task=task)


@login_required
def create_task_view():
    goals = get_goals(owner=current_user.id, include_top_level=False)

    form = CreateTaskForm(request.form)
    form.associated_goal.choices = goals['display']
    if request.method == 'POST' and form.validate():
        associated_goal_name = None
        for goal in goals['basic']:
            if form.associated_goal.data == goal[0]:
                associated_goal_name = goal[1]
                break

        if associated_goal_name is None:
            # Should only happen if a page was left open long enough for
            # the location to be deleted in a separate session
            flash(
                'Associated goal not found, cannot create task.',
                'danger',
            )
            return redirect(url_for('create_task'))

        new_task = Task.create(
            name=form.task_name.data,
            associated_goal_id=form.associated_goal.data,
            owner_id=current_user.id,
        )

        if new_task is None:
            flash(
                'Task %s already exists under %s!' % (
                    form.task_name.data,
                    associated_goal_name,
                ),
                'danger',
            )
            return redirect(url_for('create_task'))
        else:
            flash(
                'Task %s created under %s!' % (
                    form.task_name.data,
                    associated_goal_name,
                ),
                'success',
            )
            return redirect(url_for('home'))
    else:
        return render_template("task.html", form=form)
