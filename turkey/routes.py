from turkey import app
from turkey.auth import (login_view, logout_view, register_view,
                         my_account_view)
from turkey.goal import create_goal_view
from turkey.task import (
    create_task_view,
    complete_task_view,
    complete_old_task_view,
    task_history_view,
)
from turkey.home import home_view
from turkey.errors import not_found_view, not_allowed_view
from turkey.site_admin import site_admin_view

app.add_url_rule(
    '/',
    'home',
    home_view,
    methods=['GET'],
)
app.add_url_rule(
    '/admin',
    'admin',
    site_admin_view,
    methods=['GET', 'POST'],
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
    '/task_history/<task_id>',
    'task_history',
    task_history_view,
    methods=['GET'],
)
app.add_url_rule(
    '/complete_old_task/<task_id>/<task_date>',
    'complete_old_task',
    complete_old_task_view,
    methods=['GET', 'POST'],
)
app.add_url_rule(
    '/me',
    'me',
    my_account_view,
    methods=['GET', 'POST'],
)

app.error_handler_spec[None][403] = not_allowed_view
app.error_handler_spec[None][404] = not_found_view
