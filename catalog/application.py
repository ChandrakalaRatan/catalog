#!/usr/bin/env python
"""Main Python script that starts the catalog app.
It checks to see if the database file exists and if not it creates the database
and populates it with some sample content, for demonstration purposes.
"""
import os.path
from catalog import app
from catalog.database_setup import createDB
from catalog.populate_data import populateData

if __name__ == '__main__':
    # App configuration
    app.config['DATABASE_URL'] = 'sqlite:///womenswearcatalog.db'
    # app.config['DATABASE_URL'] = 'postgresql://catalog:udacity'
    #                               '@localhost/catalog'
    app.config['UPLOAD_FOLDER'] = '/vagrant/catalog/catalog/item_images'
    app.config['OAUTH_SECRETS_LOCATION'] = ''
    app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg', 'png', 'gif'])
    app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4 MB
    app.secret_key = 'super_secret_key'

    if app.config['DATABASE_URL'] == 'sqlite:///womenswearcatalog.db':
        if os.path.isfile('womenswearcatalog.db') is False:
            createDB(app.config['DATABASE_URL'])
            populateData()
    else:  # for postgresql
        createDB(app.config['DATABASE_URL'])
        populateData()

    app.debug = True
    app.run(host='0.0.0.0', port=5000)
