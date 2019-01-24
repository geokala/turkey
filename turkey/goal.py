from flask_login import login_required, current_user
from turkey.models import Goal
from flask import request, redirect, url_for, flash
from wtforms import Form, TextField, validators, SelectField
from turkey.utils import int_or_null, get_goals, render_turkey


class GoalForm(Form):
    goal_name = TextField(
        'Goal name',
        [
            validators.Length(max=255),
            validators.Required(),
        ],
    )
    parent_goal = SelectField(
        'Parent goal',
        coerce=int_or_null,
    )


@login_required
def create_goal_view():
    goals = get_goals(owner=current_user.id)

    form = GoalForm(request.form)
    form.parent_goal.choices = goals['display']
    if request.method == 'POST' and form.validate():
        parent_goal_name = None
        for goal in goals['basic']:
            if form.parent_goal.data == goal[0]:
                parent_goal_name = goal[1]
                break

        if parent_goal_name is None:
            # Should only happen if a page was left open long enough for
            # the location to be deleted in a separate session
            flash(
                'Parent goal not found, cannot create goal.',
                'danger',
            )
            return redirect(url_for('create_goal'))

        new_goal = Goal.create(
            name=form.goal_name.data,
            parent_goal_id=form.parent_goal.data,
            owner_id=current_user.id,
        )

        if new_goal is None:
            flash(
                'Goal %s already exists under %s!' % (
                    form.goal_name.data,
                    parent_goal_name,
                ),
                'danger',
            )
            return redirect(url_for('create_goal'))
        else:
            flash(
                'Goal %s created under %s!' % (
                    form.goal_name.data,
                    parent_goal_name,
                ),
                'success',
            )
            return redirect(url_for('home'))
    else:
        return render_turkey("goal.html", form=form)
