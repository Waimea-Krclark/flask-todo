#===========================================================
# App Creation and Launch
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html
import datetime

from app.helpers.session import init_session
from app.helpers.db import connect_db
from app.helpers.errors import register_error_handlers, not_found_error
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now


# Create the app
app = Flask(__name__)

# Configure app
init_datetime(app)  # Handle UTC dates in timestamps

# Setup a session for messages, etc.
init_session(app)

# Handle 404 and 500 errors
register_error_handlers(app)


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    with connect_db() as client:
        # Get all the tasks from the DB
        sql = "SELECT * FROM tasks ORDER BY priority DESC"
        result = client.execute(sql)
        tasks = result.rows
        
        # And show them on the page
        return render_template("pages/home.jinja", tasks=tasks)

#-----------------------------------------------------------
# Route for adding a task, using data posted from a form
#-----------------------------------------------------------
@app.post("/add")
def add_a_task():
    # Get the data from the form
    name  = request.form.get("name")
    priority = request.form.get("priority")

    # Sanitise the inputs
    name = html.escape(name)
    priority = html.escape(priority)

    with connect_db() as client:
        # Add the task to the DB
        sql = "INSERT INTO tasks (name, priority) VALUES (?, ?)"
        values = [name, priority]
        client.execute(sql, values)

        # Go back to the home page
        flash(f"Task '{name}' added", "success")
        return redirect("/")


#-----------------------------------------------------------
# Route for deleting a task, Id given in the route
#-----------------------------------------------------------
@app.post("/delete/<int:id>")
def delete_a_task(id):
    with connect_db() as client:
        # Delete the task from the DB
        sql = "DELETE FROM tasks WHERE id=?"
        values = [id]
        client.execute(sql, values)

        # Go back to the home page
        flash("Task deleted", "warning")
        return redirect("/")


#-----------------------------------------------------------
# Route for changing task completion, Id given in the route
#-----------------------------------------------------------

@app.post("/toggle/<int:id>")
def change_task_completion(id):
    with connect_db() as client:
        # Change the task from the DB
        sql = """
            UPDATE tasks
            SET complete = NOT complete
            WHERE id = ?;
            """
        values = [id]
        client.execute(sql, values)
        # Go back to the home page
        return redirect("/")
    
