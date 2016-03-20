from collections import OrderedDict

# Reverse order to show newest at the top, please!
version_history = OrderedDict([
    ('1.1.9', 'Fix task ordering on active tasks page properly this time.'),
    ('1.1.8', 'More IDs for tasks, breaks, etc.'),
    ('1.1.7', 'Fix task ordering on archived tasks page.'),
    ('1.1.6', 'Fix task ordering on active tasks page.'),
    ('1.1.5', (
        'Start ordering tasks for some displays, add extra IDs to tasks on '
        'active tasks page.'
    )),
    ('1.1.4', 'Fix ID for my user link'),
    ('1.1.3', 'Update more IDs to work on tests.'),
    ('1.1.2', 'Update IDs for some buttons.'),
    ('1.1.1', 'Do not allow task to be completed before it was created.'),
    ('1.1.0', 'Add version history display'),
    ('1.0.1', 'Fix display of completed tasks on active page.'),
    ('1.0.0', (
        'First versioned release. '
        'Can create goals (optionally with subgoals), '
        'and daily tasks under those goals. '
        '7 day history visible on active tasks (home) page. '
        'Full history can be viewed on task history page. '
        'Can set missed days as breaks (e.g. due to absence/illness). '
        'Can archive tasks when they are finished.'
    )),
])
current_version = list(version_history.keys())[0]
