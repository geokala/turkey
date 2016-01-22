from flask import render_template


def not_found_view(error):
    return render_template('errors/404.html'), 404
