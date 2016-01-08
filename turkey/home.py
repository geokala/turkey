from flask import render_template, request
from turkey import app
from turkey.db import Goal, Task
from turkey.utils import get_goals
from wtforms import Form, IntegerField, validators


def make_goal_branch(this_goal, goals, tasks):
    result = {
        'goals': {},
        'tasks': [],
    }
    for task in tasks:
        if task.associated_goal_id == this_goal[0]:
            result['tasks'].append(task)
    for goal in goals:
        if goal.parent_goal_id == this_goal[0]:
            next_goal = (goal.id, goal.name)
            result['goals'][next_goal] = make_goal_branch(
                next_goal,
                goals,
                tasks,
            )
    return result


@app.route("/")
def home_view():
    tasks = {}
    goals = Goal.query.all()
    tasks = Task.query.all()

    tree = {'goals': {}}

    top_level_goals = [
        (goal.id, goal.name)
        for goal in goals
        if goal.parent_goal_id is None
    ]

    for goal in top_level_goals:
        tree['goals'][goal] = make_goal_branch(
            goal,
            goals,
            tasks,
        )

    return render_template("home.html", tree=tree)
