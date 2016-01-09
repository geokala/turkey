from turkey import app
from turkey.auth import (login_view, logout_view, register_view,
                         my_account_view)
from turkey.goal import create_goal_view
from turkey.task import create_task_view, complete_task_view
from turkey.home import home_view

app.add_url_rule(
    '/',
    'home',
    home_view,
    methods=['GET'],
)
app.add_url_rule(
    '/login',
    'login',
    login_view,
    methods=['GET', 'POST'],
)
app.add_url_rule(
    '/logout',
    'logout',
    logout_view,
)
app.add_url_rule(
    '/register',
    'register',
    register_view,
    methods=['GET', 'POST'],
)
app.add_url_rule(
    '/create_goal',
    'create_goal',
    create_goal_view,
    methods=['GET', 'POST'],
)
app.add_url_rule(
    '/create_task',
    'create_task',
    create_task_view,
    methods=['GET', 'POST'],
)
app.add_url_rule(
    '/complete_task/<task_id>',
    'complete_task',
    complete_task_view,
    methods=['GET', 'POST'],
)
app.add_url_rule(
    '/me',
    'me',
    my_account_view,
    methods=['GET', 'POST'],
)
