from collections import OrderedDict

# Reverse order to show newest at the top, please!
version_history = OrderedDict([
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
