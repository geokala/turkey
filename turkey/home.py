from flask.ext.login import current_user
from flask import render_template
from turkey import app
from turkey.models import Goal, Task, CompletedTask
import datetime
import calendar


def get_last_week_completed_tasks(task_id):
    current_day = datetime.date.today()
    midnight = datetime.datetime.min.time()
    current_day = datetime.datetime.combine(current_day, midnight)
    one_week_ago = current_day - datetime.timedelta(days=6)

    days_ago = [
        current_day,
        current_day - datetime.timedelta(days=1),
        current_day - datetime.timedelta(days=2),
        current_day - datetime.timedelta(days=3),
        current_day - datetime.timedelta(days=4),
        current_day - datetime.timedelta(days=5),
        current_day - datetime.timedelta(days=6),
    ]

    task_created = Task.query.filter(
        Task.owner_id == current_user.id,
        Task.id == task_id,
    ).one()
    creation_date = task_created.creation_time
    creation_day = datetime.datetime.combine(creation_date, midnight)

    all_completed = CompletedTask.query.filter(
        CompletedTask.associated_task_id == task_id,
        CompletedTask.completed_time >= days_ago[6],
    ).all()

    week = []
    for day in days_ago:
        finished = False
        task_completed = False
        if day < creation_day:
            # This is before it was created
            finished = True
        for completed in all_completed:
            if completed.completed_time >= day:
                next_day = day + datetime.timedelta(days=1)
                if completed.completed_time < next_day:
                    task_completed = True
                    # We found a completion record for this one, stop looking
                    break
        if finished:
            break
        else:
            week.append({
                'name': calendar.day_name[day.weekday()],
                'completed': task_completed,
            })

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

    # Stripe alternating sections for visibility
    striped = False
    for day in week:
        day['striped'] = striped
        striped = not striped

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
                'last_week': get_last_week_completed_tasks(task.id),
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
