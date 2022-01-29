# %%
from pkg_resources import Requirement
from flask import (
    render_template,
    url_for,
    flash,
    redirect,
    session,
    stream_with_context,
)
from flask_login import login_user, current_user, logout_user, login_required
import io
import os
import sys

# %%
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
from pgdxapp import app, bcrypt, admin, elio_dir, req_dir
from pgdxapp.forms import (
    LoginForm,
    SetupForm,
    GoForm,
    ConfirmForm,
    FinalForm,
)

# %%
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from pgdx_reporting import setup

# (
#     check_batch_name,
#     get_dir_from_batch,
#     latest_batch_directory,
#     check_batch_already_run,
# )
from pgdx_reporting.process import pgdx_process


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    if current_user.is_authenticated:
        return redirect(url_for("begin"))
    form = LoginForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(admin.hashed_password, form.password.data):
            login_user(admin, remember=form.remember.data)
            flash("You have been logged in!", "success")
            return redirect(url_for("begin"))
        else:
            flash("Login Unsuccessful. Please check password", "danger")
    return render_template("home.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("You have successfully logged out.", "info")
    return redirect(url_for("home"))


@app.route("/begin", methods=["GET", "POST"])
@login_required
def begin():
    form = GoForm()
    if form.validate_on_submit():
        if form.process_latest.data:
            session["latest"] = True
            session["batch"] = None
            batch_dir = setup.latest_batch_directory(elio_dir)
            if batch_dir:
                session["batch_dir"] = os.path.join(elio_dir, batch_dir)
                check = setup.check_batch_already_run(session["batch_dir"])
                if check:
                    return redirect(url_for("confirm"))
                else:
                    return redirect(url_for("process"))
            else:
                flash("Error", "danger")
        else:
            flash("Error", "danger")
    return render_template("begin.html", form=form)


@app.route("/enterbatch", methods=["GET", "POST"])
@login_required
def enterbatch():
    form = SetupForm()
    if form.validate_on_submit():
        if form.batch.data:
            session["latest"] = False
            session["batch"] = form.batch.data
            check = setup.check_batch_name(session["batch"])
            if check:
                candidate = setup.get_dir_from_batch(elio_dir, check)
                if candidate:
                    session["batch_dir"] = os.path.join(elio_dir, candidate)
                    check = setup.check_batch_already_run(session["batch_dir"])
                    print(check)
                    if check:
                        return redirect(url_for("confirm"))
                    else:
                        return redirect(url_for("process"))
                else:
                    flash("Cannot find that batch. Try again.", "danger")
            else:
                flash("Batch format seems wrong. Try again.", "danger")
        else:
            flash("Please enter a batch ID!", "danger")
    return render_template("enterbatch.html", form=form)


@app.route("/confirm", methods=["GET", "POST"])
@login_required
def confirm():
    form = ConfirmForm()
    if form.validate_on_submit():
        if form.yes.data:
            return redirect(url_for("process"))
        else:
            flash("Error", "danger")
    return render_template("confirm.html", form=form)


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    # rv.enable_buffering(3)
    return rv


@app.route("/process", methods=["GET", "POST"])
@login_required
def process():
    form = FinalForm()
    if form.validate_on_submit():
        if form.yes.data:
            flash(
                (
                    "Note: Do not reload or refresh "
                    "this page during processing. "
                    "It will restart the process. "
                    "Log out or close the window upon completion."
                ),
                "danger",
            )
            with app.app_context():

                def func():
                    """
                    This function takes the pgdx_process function and 
                    converts all print statements into yields 
                    """
                    yield ("Starting up ...")

                    try:
                        _stdout = sys.stdout
                        sys.stdout = output = io.StringIO()
                        pgdx_process(session["batch_dir"], req_dir)
                        output.seek(0)
                        for line in output:
                            sys.stdout = _stdout
                            yield "{}".format(line.strip("\n"))
                            sys.stdout = output
                    finally:
                        sys.stdout.close()  # close the StringIO object
                        sys.stdout = _stdout  # restore sys.stdout

                return app.response_class(
                    stream_with_context(
                        stream_template(
                            "process.html", result=func(), form=form, going=True
                        )
                    )
                )
    else:
        return render_template("process.html", form=form, going=False)

