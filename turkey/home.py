from flask.ext.login import current_user
from flask import render_template
from turkey import app
from turkey.models import Goal, Task, CompletedTask


def make_goal_branch(this_goal, goals, tasks, completed):
    result = {
        'goals': {},
        'open_tasks': [],
        'completed_tasks': [],
    }
    for task in tasks:
        # Put the tasks in two lists so we show the open tasks first, then the
        # completed
        if task.associated_goal_id == this_goal[0]:
            task_dict = {
                'name': task.name,
                'id': task.id,
            }
            if task.id in completed:
                task_dict['completed'] = True
                result['completed_tasks'].append(task_dict)
            else:
                task_dict['completed'] = False
                result['open_tasks'].append(task_dict)
        result['tasks'] = result['open_tasks'] + result['completed_tasks']
    for goal in goals:
        if goal.parent_goal_id == this_goal[0]:
            next_goal = (goal.id, goal.name)
            result['goals'][next_goal] = make_goal_branch(
                next_goal,
                goals,
                tasks,
                completed,
            )
    return result


@app.route("/")
def home_view():
    if current_user.is_anonymous:
        goals = []
        tasks = []
        completed = []
    else:
        goals = Goal.query.filter(
            Goal.owner_id == current_user.id,
        ).all()
        tasks = Task.query.filter(
            Task.owner_id == current_user.id,
        ).all()
        completed = CompletedTask.get_completed_today()

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
            completed,
        )

    return render_template("home.html", tree=tree)
