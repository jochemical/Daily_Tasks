# Imports
import datetime
import uuid
from collections import defaultdict
from flask import (
    Blueprint, 
    current_app, 
    request, 
    render_template, 
    redirect, 
    url_for
)

# Create blueprints:
pages = Blueprint("habits", __name__, template_folder="templates", static_folder="static")
# "habbits" is the name of the blueprint, which we have to use each time we use url_for !
# __name__ has to be the importname of the blueprint
# We also define the template_folder and the static_folder to create the correct url's
# If you don't add these folders, blueprint will not have acces to these folders
# Now we have to replace 'app' for 'pages' in all of our endpoints
# Later on we import the blueprint in our Flaks-app in app.py


# Context_processor
# Using the context_processer we do not have to pass in a date_range-function,
# each time we render a template.
@pages.context_processor
def add_calc_date_range():
    def date_range(start: datetime.datetime):
        # List comprehension
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4) ]
        return dates
    return {"date_range": date_range}

# This function only makes sure every date will have a timeset of midnight
def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)

# Route for index-page:
@pages.route("/")
def index():
    # Abstract the date from the URL if present
    date_str = request.args.get("date")

    if date_str:
        # fromisformat(date_str) creates a date-object (in iso-format) from a string
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        # If the URL contains no date, the date of today will be selected
        selected_date = today_at_midnight()

    # Here we use the habbits collecion:
    habits_on_date = current_app.db.habits.find({"added": {"$lte": selected_date} } )
    # "$lte" less then or equal to , is a query
    # habbits_on_date is a list of dictionaries

    # Listcomprehension:
    completions = [
        habit["habit"] 
        for habit in current_app.db.completions.find( {"date": selected_date} )
    ]

    return render_template(
        "index.html", 
        habits=habits_on_date, 
        title="Habit Tracker - Home",  
        # We pass in a function during selected_date
        selected_date = selected_date,
        completions=completions
        )


# Route for adding an task/habit:
@pages.route("/add", methods=["GET", "POST"])
def add_habit():
    # Include today's date at midnight
    today = today_at_midnight()

    # Add new habit to database:
    if request.form:
        # uuid.uuid4().hex creates a unique random id-nr.
        current_app.db.habits.insert_one(
            {"_id": uuid.uuid4().hex, "added": today, "name": request.form.get("habit") }
        )

    return render_template(
        "add_task.html", 
        title="Habit Tracker - Add Habit", 
        selected_date=today 
        )

# Route for completing a task
# @app.post("/complete") does the same thing
@pages.route("/complete", methods=["POST"])
def complete():
    date_string = request.form.get("date")
    habit = request.form.get("habitId")
    date = datetime.datetime.fromisoformat(date_string)
    
    # Add completed habbit to our database:
    # Completions is the collection in the database
    current_app.db.completions.insert_one( {"date":date, "habit": habit} )

    return redirect(url_for("habits.index", date=date_string))
