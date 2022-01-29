from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "cee90fe7587228aa0a311a171a13dc31"
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "home"
login_manager.login_message_category = "info"

# check which machine we're running on!
try:
    comp = os.uname()[1]
except:
    comp = "server"

if comp == "AdamP51s":
    # testing environment == my laptop lolz
    run_dir = os.path.abspath(
        "/mnt/c/Users/adzab/OneDrive - Mass General Brigham/Operations/PGDx/pgdx"
    )
    req_dir = os.path.abspath(
        os.path.join(
            "/mnt/c/Users/adzab/OneDrive - Mass General Brigham/Operations/PGDx/pgdx/.Bioinformatics",
            "requirements",
        )
    )
else:
    # production environment
    run_dir = os.path.abspath("/mnt/pgdx_v1")
    req_dir = os.path.abspath("/var/www/pgdx-web-app/requirements")

elio_dir = os.path.join(run_dir, "ElioConnect_Output")


# Define a class for our one user
# Password was hashed with Bcrypt.generate_password_hash(<pw>)
class User(UserMixin):
    id = 1
    username = "admin"
    hashed_password = "$2b$12$014MwSGb8TkhibmlDFg79eWIBJXn3Dklgjv82aJK/OG0oNHDqEnwa"

    def __repr__(self):
        return "admin"


# Instantiate our user
admin = User()

# Normally this would load any user but here
# we're just using it to load admin
@login_manager.user_loader
def load_user(user_name):
    return admin


from pgdxapp import routes
