#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, 'vagrant/catalog')

from catalog import app as application
from catalog.database_setup import createDB
from catalog.populate_data import populateData

application.secret_key = 'super_secret_key'
application.config['DATABASE_URL'] = 'postgresql://catalog:udacity'
'@localhost/catalog'
application.config['UPLOAD_FOLDER'] = '/vagrant/catalog/item_images'
application.config['OAUTH_SECRETS_LOCATION'] = '/vagrant/catalog/'
application.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg', 'png', 'gif'])
application.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4 MB

# Create database and populate it, if not already done so.
createDB(application.config['DATABASE_URL'])
populateData()
