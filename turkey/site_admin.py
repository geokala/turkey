from flask_login import login_required, current_user
from turkey.models import SiteAdmin
from flask import request, redirect, url_for, flash, abort
from wtforms import BooleanField, Form
from sqlalchemy.orm.exc import NoResultFound
from turkey.utils import registrations_allowed, render_turkey


class SiteAdminForm(Form):
    registration_enabled = BooleanField()


@login_required
def site_admin_view():
    if not current_user.is_admin:
        abort(403)

    registration_enabled = registrations_allowed()

    form = SiteAdminForm(request.form)
    if request.method == 'POST' and form.validate():
        SiteAdmin.user_registration(
            allowed=form.registration_enabled.data,
        )

        if form.registration_enabled.data:
            message = "User registrations allowed!"
        else:
            message = "User registrations prohibited!"

        flash(
            message,
            'success',
        )
        return redirect(url_for('home'))
    else:
        form.registration_enabled.default = registration_enabled
        return render_turkey("site_admin.html", form=form)
