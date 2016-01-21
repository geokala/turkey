from turkey.models import Goal, Task, CompletedTask
import datetime
import calendar
from flask.ext.login import current_user


def int_or_null(data):
    if data == 'None':
        return None
    else:
        return int(data)


def get_goals(owner, include_top_level=True):
    all_goals = {
        goal.id: {
            'name': goal.name,
            'parent': goal.parent_goal_id,
        }
        for goal in Goal.query.filter(
            Goal.owner_id == owner,
        ).all()
    }

    # Format the goals in a useful manner
    goals = [
        (goal, details['name'])
        for goal, details in all_goals.items()]
    # Add the top level
    if include_top_level:
        goals.append((None, '-'))

    # Make the goals easier to read
    display_goals = []
    for goal in goals:
        goal_id = goal[0]
        goal_name = []
        next_id = goal_id
        while next_id is not None:
            goal_name.append(all_goals[next_id]['name'])
            next_id = all_goals[next_id]['parent']
        goal_name.reverse()
        goal_name = '/'.join(goal_name)
        if goal_name == '':
            goal_name = '-'
        display_goals.append((goal_id, goal_name))

    return {
        'basic': goals,
        'display': display_goals,
    }


def get_days_ago_list(days):
    current_day = datetime.date.today()
    midnight = datetime.datetime.min.time()
    current_day = datetime.datetime.combine(current_day, midnight)

    days_ago = []
    for day in range(0, days + 1):
        days_ago.append(current_day - datetime.timedelta(days=day))

    return days_ago


def get_completed_tasks_history(task_id, days=6):
    """
        Default to getting the last week's completed tasks.
    """
    midnight = datetime.datetime.min.time()
    days_ago = get_days_ago_list(days=days)

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

    history = []
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
                    completed_comment = completed.comment
                    # We found a completion record for this one, stop looking
                    break
        if finished:
            break
        else:
            history.append({
                'name': calendar.day_name[day.weekday()],
                'completed': task_completed,
                'date': day.strftime('%Y %b %d'),  # e.g. 2016 Jan 21
                'id': task_id,
                'comment': completed_comment,
            })

    return history
