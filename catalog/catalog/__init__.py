from flask import Flask

# Initialise the Flask app object
app = Flask(__name__)

# Import modules that have the route() decorator in them.
import catalog.views
import catalog.json_endpoints
import catalog.Oauth
