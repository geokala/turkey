from turkey import app
from turkey.utils import render_turkey


@app.errorhandler(404)
def not_found_view(error):
    return render_turkey('errors/404.html'), 404


@app.erorrhandler(403)
def not_allowed_view(error):
    return render_turkey('errors/403.html'), 403
