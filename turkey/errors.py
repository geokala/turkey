from turkey.utils import render_turkey


def not_found_view(error):
    return render_turkey('errors/404.html'), 404


def not_allowed_view(error):
    return render_turkey('errors/403.html'), 403
