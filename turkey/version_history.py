from turkey.utils import render_turkey
from turkey.version import version_history

def version_history_view():
    return render_turkey("version_history.html", version_history=version_history)
