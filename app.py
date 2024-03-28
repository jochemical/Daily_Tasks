# Imports
from flask import Flask

# The next three imports are necessarry for the MongoDB-database
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Here we import the blueprints we need:
from routes import pages

# The next line is needed to load our the MONGODB_URI in our environment-variables (.env)
load_dotenv()


# Flask calls the create_app-method automatically when Flask is run
def create_app(): 
    # Here we create our Flask app
    app = Flask(__name__)

    # First we create a client for our database
    # Here we use the os-library to get the variables stored within the virtual environment
    client = MongoClient( os.environ.get("MONGODB_URI") ) 

    # Next we set up our database for the app
    # 'tracker' is the name of the database (not the cluster, nor its (sub)collections)
    app.db = client.tracker
    # client.get_default_database() seems to cause problems
  
    # Here we register our blueprints and add them to our Flask app
    app.register_blueprint(pages)

    # For Flaks, we need to return the app
    return app
