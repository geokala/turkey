from flask.ext.login import login_required, current_user
from turkey.models import Task, CompletedTask
from sqlalchemy.orm.exc import NoResultFound
from flask import request, render_template, redirect, url_for, flash
from wtforms import Form, TextField, validators, SelectField, TextAreaField
from turkey.utils import int_or_null, get_goals
import datetime


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


@login_required
def complete_task_view(task_id):
    form = CompleteTaskForm(request.form)

    try:
        Task.query.filter(
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
        completed_task = CompletedTask.create(
            comment=form.task_comment.data,
            associated_task_id=task_id,
            completed_time=datetime.datetime.now(),
            owner_id=current_user.id,
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
    else:
        # TODO: Make complete task page show which task it thinks is being
        # completed
        return render_template("complete_task.html", form=form)


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
