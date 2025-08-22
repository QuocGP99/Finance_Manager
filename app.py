from flask import Flask, render_template, request, redirect, url_for, flash
import os
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate



app = Flask(__name__, template_folder="templates")


db = SQLAlchemy(app)
migrate = Migrate(app, db)




    

