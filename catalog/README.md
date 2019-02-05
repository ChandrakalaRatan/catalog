# Item Catalog Project

Item Catalog project is a web application developed by utilizing the Flask framework which accesses a SQL database to populate data. It also uses third party authentication like  google and facebook application.

# About
This application provides Women Exclusive Store details that stores the details of women's clothing and accessories. Currently it contains 6 categories. The user can login via Facebook or google in order to create new Items. They can create, edit and delete the data if they are logged in. It also restricts from deleting other's data.

# Features
	Google and facebook authentication and authorisation check.
	Full CRUD support using SQLAlchemy and Flask framework.
	JSON endpoints.

# Project Structure
	.
	├── g_client_secrets.json
	├── fb_client_secrets.json
	├── catalog.ini
	├── catalog.wsgi
	├── womenswearcatalog.db
	├── application.py
	├── README.md
	├── requirements.txt
	├── Vagrantfile
	├── catalog
		├── database_setup.py
		├── dbconnect.py
		├──  __init__.py
		├── json_endpoints.py
		├── Oauth.py
		├── populate_data.py
		├── views.py
		├── static
		│   ├── css
		│   │   └──cssstyle.css
		│   ├── js
		│   │   └──js.cookie-2.0.4.min.js
		│   └── mdl
		│       ├── material.css
		│       ├── material.js
		│       ├── material.min.css
		│       ├── material.min.css.map
		│       ├── material.min.js
		│       └──material.min.js.map
		└── templates
			├── add_item_button.html
			├── catalog_homepage.html
			├── create_new_item.html
			├── delete_item.html
			├── edit_item.html
			├── layout.html
			├── login.html
        		├── show_catalog_item.html
        		├── show_item.html
        		└── show_my_catalog_items.html
		
		
# Required Libraries and Dependencies
The project code requires the following software:

	#### Python 2.7.x
	#### SQLAlchemy 0.8.4 or higher (a Python SQL toolkit)
	#### Flask 0.10.1 or higher (a web development microframework)
	#### HTML, CSS, Bootstrap, SQLite

The following Python packages:
	#### requests
	#### httplib2

# How to Run the Project

	1. Download and install Vagrant.

	2. Download and install VirtualBox.

	3. Clone or download the Vagrant VM configuration file from here.

	4. Open the above directory and navigate to the vagrant/ sub-directory.

	5. Open terminal, and type

	   #### vagrant up

	   This will cause Vagrant to download the Ubuntu operating system and 
       install it. This may take quite a while depending on how fast your 
       Internet connection is.

	6. After the above command succeeds, connect to the newly created VM 
      by typing the following command:

	 	#### vagrant ssh

	7. Go to the project directory
        
	    	#### cd /vagrant/ to navigate to the shared repository.

	8. Download or clone this repository, and navigate to it.

	9. Run the following command to install depedencies
	     	
		#### pip  install  -r  requirements.txt

	10. Run the following command to run the application:

		#### python application.py

	11. Open http://localhost:5000/ in your favourite Web browser.

# JSON Endpoints
The following are open to the public:

## JSON end points to display all items in all catalog
	#### /catalog/JSON

## JSON end points to display all items belongs to a specific category in the catalog
   	#### /catalog/category/<category_id>/items/JSON

## JSON end points to display specific item belong to a specific category in the catalog.
	#### /catalog/category/<int:category_id>/item/<int:item_id>/JSON

## JSON end points to display all items belongs to a specific user in the catalog
    	#### /catalog/user/<user_id>/items/JSON
 
## JSON end points to display all user
   	#### /catalog/users/JSON
