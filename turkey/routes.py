from turkey import app
from turkey.auth import (login_view, logout_view, register_view,
                         my_account_view)
from turkey.goal import create_goal_view
from turkey.task import (
    create_task_view,
    complete_task_view,
    complete_old_task_view,
    task_history_view,
    confirm_archive_task_view,
)
from turkey.task_break import task_break_view
from turkey.archived_tasks import archived_tasks_view
from turkey.home import home_view
from turkey.site_admin import site_admin_view
from turkey.version_history import version_history_view

app.add_url_rule(
    '/',
    'home',
    home_view,
    methods=['GET'],
)
app.add_url_rule(
    '/version_history',
    'version_history',
    version_history_view,
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
    '/archived_tasks',
    'archived_tasks',
    archived_tasks_view,
    methods=['GET'],
)
app.add_url_rule(
    '/confirm_archive_task/<task_id>',
    'confirm_archive_task',
    confirm_archive_task_view,
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
    '/task_break/<task_id>/<task_date>',
    'task_break',
    task_break_view,
    methods=['GET', 'POST'],
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
