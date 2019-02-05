import os
import logging
from flask import render_template, request
from flask import redirect, url_for, flash
from flask import send_from_directory
from flask import session as login_session
from werkzeug import secure_filename
from sqlalchemy import desc, literal
from sqlalchemy.orm.exc import NoResultFound

from catalog import app
from catalog.database_setup import Category, Item, User
from catalog.dbconnect import dbconnect
from catalog.Oauth import getUserID


# function to call catalog home page displays 10 recently added items
@app.route('/')
@app.route('/catalog/')
def showCatalogHome():
    """Show the homepage displaying the women clothings and latest items.
    Returns:
        A web page with the 10 latest items that have added.
    """
    session = dbconnect()
    categories = session.query(Category).all()
    latest_items = session.query(Item).order_by(desc(Item.id))[0:10]
    session.close()
    return render_template('catalog_homepage.html',
                           categories=categories,
                           latest_items=latest_items)


# function to display all the items for particular category on the menu
@app.route('/catalog/<category_name>/items/')
def showCatalogItems(category_name):
    """Show items belonging to a specified category.
    Args:
        category_name (str): The name of the category to which the item
            belongs.
    Returns:
        A web page showing all the items in the specified category.
    """
    session = dbconnect()
    try:
        category = session.query(Category).filter_by(name=category_name).one()
    except NoResultFound:
        flash("The category '%s' does not exist." % category_name)
        return redirect(url_for('showCatalogHome'))

    categories = session.query(Category).all()
    items = (session.query(Item).filter_by(category=category).
             order_by(Item.name).all())

    session.close()
    if not items:
        flash("There are currently no items in this category.")
    return render_template('show_catalog_item.html',
                           categories=categories,
                           category=category,
                           items=items)


# function to MyCollection page which shows items added by
# currently logined User
@app.route('/catalog/myitems/')
def showMyCatalogItems():
    """If logged in, show the user the items they have added."""
    if 'username' not in login_session:
        return redirect('/login')

    userid = getUserID(login_session['email'])

    session = dbconnect()
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(user_id=userid).all()
    session.close()

    if not items:
        flash("You haven't add any items yet.")
        redirect(url_for('showCatalogHome'))
    return render_template('show_my_catalog_items.html',
                           categories=categories,
                           items=items)


# function to show the details of an item
@app.route('/catalog/<category_name>/<item_name>/')
def showItem(category_name, item_name):
    """Show details of a particular item belonging to a specified category.
    Args:
        category_name (str): The name of the category to which the item
            belongs.
        item_name (str): The name of the item.
    Returns:
        A web page showing information of the requested item.
    """
    session = dbconnect()
    try:
        category = session.query(Category).filter_by(name=category_name).one()
    except NoResultFound:
        flash("The category '%s' does not exist." % category_name)
        session.close()
        return redirect(url_for('showCatalogHome'))

    try:
        item = session.query(Item).filter_by(name=item_name).one()
    except NoResultFound:
        flash("The item '%s' does not exist." % item_name)
        session.close()
        return redirect(url_for('showCatalogItems',
                                category_name=category_name))

    user = session.query(User).filter_by(id=item.user_id).one()
    ower_name = user.name

    categories = session.query(Category).all()
    session.close()
    return render_template('show_item.html',
                           categories=categories,
                           category=category,
                           item=item,
                           ower_name=ower_name)


# function to create a new item
@app.route('/catalog/new/', methods=['GET', 'POST'])
def createNewItem():
    """Allow users to create a new item in the catalog."""
    if 'username' not in login_session:
        return redirect('/login')

    session = dbconnect()

    if request.method == 'POST':
        if not request.form['name']:
            flash("New item not created: No name provided.")
            return redirect(url_for('showCatalogHome'))

        if request.form['name'] == "items":
            flash("Error: Can't have an item called 'items'.")
            return redirect(url_for('showCatalogHome'))

        # make sure item names are unique
        qry = session.query(Item).filter(Item.name == request.form['name'])
        already_exists = (session.query(literal(True)).
                          filter(qry.exists()).scalar())
        if already_exists is True:
            flash("Error: There is already an item with the name '%s'"
                  % request.form['name'])
            session.close()
            return redirect(url_for('showCatalogHome'))

        category = (session.query(Category)
                    .filter_by(name=request.form['category']).one())
        add_new_item = Item(category=category,
                            name=request.form['name'],
                            description=request.form['description'],
                            quantity=request.form['quantity'],
                            price=request.form['price'],
                            user_id=login_session['user_id'])

        try:
            createimagefile = request.files['file']
        except Exception:
            createimagefile = None
        try:
            createimageurl = request.form['image_url']
        except Exception:
            createimageurl = None

        if createimagefile and allowedFile(createimagefile.filename):
            filename = secure_filename(createimagefile.filename)
            if os.path.isdir(app.config['UPLOAD_FOLDER']) is False:
                os.mkdir(app.config['UPLOAD_FOLDER'])
            createimagefile.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                              filename))
            add_new_item.image_filename = filename

        elif createimageurl:
            add_new_item.image_url = request.form['image_url']

        session.add(add_new_item)
        session.commit()

        flash("New Item successfully created!")
        category_name = category.name
        item_name = add_new_item.name
        session.close()
        return redirect(url_for('showItem',
                                category_name=category_name,
                                item_name=item_name))
    else:
        categories = session.query(Category).all()

        # See, if any, which category page new item was click on.
        ref_category = None
        if request.referrer and 'catalog' in request.referrer:
            ref_url_elements = request.referrer.split('/')
            if len(ref_url_elements) > 5:
                ref_category = ref_url_elements[4]

        session.close()
        return render_template('create_new_item.html',
                               categories=categories,
                               ref_category=ref_category)


# function to edit an item
@app.route('/catalog/<category_name>/<item_name>/edit/',
           methods=['GET', 'POST'])
@app.route('/catalog/<item_name>/edit/', methods=['GET', 'POST'])
def editItem(item_name, category_name=None):
    """Edit the details of the specified item.
    Args:
        item_name (str): Name of item to be edited.
        category_name (str): Optionally, can also specify the category to
            which the item belongs to.
    """
    if 'username' not in login_session:
        flash("You need to login to edit any item.")
        return redirect('/login')

    session = dbconnect()

    try:
        item = session.query(Item).filter_by(name=item_name).one()
    except NoResultFound:
        flash("Error: The item '%s' does not exist." % item_name)
        return redirect(url_for('showCatalogHome'))

    if login_session['user_id'] != item.user_id:
        flash("You didn't add this item, so you can't edit it. Sorry :-(")

        category = session.query(Category).filter_by(id=item.category_id).one()
        category_name = category.name
        item_name = item.name
        session.close()
        return redirect(url_for('showItem',
                                category_name=category_name,
                                item_name=item_name))

    if request.method == 'POST':
        if request.form['name'] != item.name:
            # make sure that item names are unique
            qry = session.query(Item).filter(Item.name == request.form['name'])
            already_exists = (session.query(literal(True)).filter(qry.exists())
                              .scalar())
            if already_exists is True:
                original_category = (session.query(Category)
                                     .filter_by(id=item.category_id).one())
                flash("Error: There is already an item with the name '%s'"
                      % request.form['name'])
                session.close()
                return redirect(url_for('showCatalogItems',
                                        category_name=original_category.name))
            item.name = request.form['name']

        form_category = (session.query(Category)
                         .filter_by(name=request.form['category']).one())

        if form_category != item.category:
            item.category = form_category

        item.description = request.form['description']
        item.quantity = request.form['quantity']
        item.price = request.form['price']

        try:
            editimagefile = request.files['file']
        except Exception:
            editimagefile = None
        try:
            editimageurl = request.form['image_url']
        except Exception:
            editimageurl = None
        try:
            delete_image = request.form['delete_image']
        except Exception:
            delete_image = None

        if(delete_image and delete_image == 'delete'):
            if item.image_filename:
                deleteImage(item.image_filename)
                item.image_filename = None
                item.image_url = None
            elif item.image_url:
                item.image_filename = None
                item.image_url = None
                session.add(item)
                session.commit()

        if editimagefile and allowedFile(editimagefile.filename):
            if item.image_filename:
                delete_image(item.image_filename)
            filename = secure_filename(editimagefile.filename)

            if os.path.isdir(app.config['UPLOAD_FOLDER']) is False:
                os.mkdir(app.config['UPLOAD_FOLDER'])
            editimagefile.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                            filename))

            item.image_filename = filename
            item.image_url = None

        elif not editimagefile and editimageurl:
            item.image_url = request.form['image_url']
            if item.image_filename:
                deleteImage(item.image_filename)
                item.image_filename = None

        session.add(item)
        session.commit()

        flash("Item is successfully edited!")
        category_name = form_category.name
        item_name = item.name
        session.close()
        return redirect(url_for('showItem',
                                category_name=category_name,
                                item_name=item_name))
    else:
        categories = session.query(Category).all()
        session.close()
        return render_template('edit_item.html',
                               categories=categories,
                               item=item)


# function to delete an item
@app.route('/catalog/<item_name>/delete/', methods=['GET', 'POST'])
def deleteItem(item_name):
    """Delete a specified item from the database.
    Args:
        item_name (str): Name of the item to be deleted.
    """
    if 'username' not in login_session:
        return redirect('/login')

    session = dbconnect()
    try:
        item = session.query(Item).filter_by(name=item_name).one()
    except NoResultFound:
        flash("Error: The item '%s' does not exist." % item_name)
        session.close()
        return redirect(url_for('showCatalogHome'))

    if login_session['user_id'] != item.user_id:
        flash("You didn't add this item, so you can't delete it. Sorry :-(")
        category = session.query(Category).filter_by(id=item.category_id).one()
        category_name = category.name
        item_name = item.name
        session.close()
        return redirect(url_for('showItem',
                                category_name=category_name,
                                item_name=item_name))

    if request.method == 'POST':
        if item.image_filename:
            deleteImage(item.image_filename)
        session.delete(item)
        session.commit()
        category = session.query(Category).filter_by(id=item.category_id).one()

        flash("Item successfully deleted!")
        category_name = category.name
        session.close()
        return redirect(url_for('showCatalogItems',
                                category_name=category_name))
    else:
        categories = session.query(Category).all()
        session.close()
        return render_template('delete_item.html',
                               categories=categories,
                               item=item)


# function to display the image file
@app.route('/item_images/<filename>')
def showItemImage(filename):
    """Route to serve user uploaded images.
    Args:
        filename (str): Filename of the image to serve to the client.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# function to verify the file is an allowed format
def allowedFile(filename):
    """Check if the filename has one of the allowed extensions.
    Args:
        filename (str): Name of file to check.
    """
    return ('.' in filename and filename.rsplit('.', 1)[1] in
            app.config['ALLOWED_EXTENSIONS'])


# function to delete an image from the image directory
def deleteImage(filename):
    """Delete an item image file from the filesystem.
    Args:
        filename (str): Name of file to be deleted.
    """
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    except OSError:
        logging.debug("Error deleting image file %s" % filename)
