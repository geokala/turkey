from flask.ext.login import current_user
from turkey import app
from turkey.models import Goal, Task, CompletedTask
import datetime
import calendar
from turkey.utils import get_tasks_history, render_turkey


def get_completed_tasks_display(task_id):
    week = get_tasks_history(task_id)

    # Calculate widths to make 100% of progress bar for display
    width_remaining = 100
    for day in week:
        day['width'] = 100 // len(week)
        width_remaining = width_remaining - day['width']

    if len(week) > 0:
        next_day_width_balance = 0
        while width_remaining > 0:
            week[next_day_width_balance]['width'] += 1
            width_remaining -= 1
            next_day_width_balance = (next_day_width_balance + 1) % len(week)

    return week


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
                'created': task.creation_time.strftime('%Y %h %d'),
                'finished': task.finish_time.strftime('%Y %h %d'),
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


def archived_tasks_view():
    if current_user.is_anonymous:
        goals = []
        tasks = []
        completed = []
    else:
        current_time = datetime.datetime.now()
        goals = Goal.query.filter(
            Goal.owner_id == current_user.id,
        ).all()
        tasks = Task.query.filter(
            Task.owner_id == current_user.id,
        ).all()
        tasks = [
            task for task in tasks
            if task.finish_time is not None
            and task.finish_time < current_time
        ]
        completed = CompletedTask.get_completed(
            date=datetime.datetime.today(),
        )

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

    return render_turkey("archived_tasks.html", tree=tree, current_page='archived_tasks')
