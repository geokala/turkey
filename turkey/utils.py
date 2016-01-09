from turkey.db import Goal


def int_or_null(data):
    if data == 'None':
        return None
    else:
        return int(data)


def get_goals(include_top_level=True):
    all_goals = {
        goal.id: {
            'name': goal.name,
            'parent': goal.parent_goal_id,
        }
        for goal in Goal.query.all()
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
