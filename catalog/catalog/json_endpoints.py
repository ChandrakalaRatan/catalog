"""Defines JSON API endpoints."""
from flask import jsonify, redirect, url_for, flash
from sqlalchemy.orm.exc import NoResultFound

from catalog import app
from catalog.database_setup import Category, Item, User
from catalog.dbconnect import dbconnect


# Returns a JSON of all items in all categories in the catalog
@app.route('/catalog/JSON')
def allItemsJSON():
    """Returns all the items in the catalog as a JSON file.
    The for loop in the call to jsonify() goes through each category and,
    because the Category class has a reference to the items in it, for each
    item a call to its serialise function is made. So we end up with a JSON
    array of items for each category.
    """
    session = dbconnect()
    categories = session.query(Category).all()
    serialised_catergories = [i.serialise for i in categories]
    session.close()
    return jsonify(Category=serialised_catergories)


# Returns a JSON of all items for a specific category in the catalog
@app.route('/catalog/category/<category_id>/items/JSON')
def categoryItemsJSON(category_id):
    session = dbconnect()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category=category).all()
    session.close()
    return jsonify(items=[i.serialise for i in items])


# Returns a JSON of a specific item belong to a specific
# category in the catalog.
@app.route('/catalog/category/<int:category_id>/item/<int:item_id>/JSON')
def itemJSON(item_id, category_id):
    """Returns a single item in a JSON file.
    Args:
        item_id (int): The id of the item to return in JSON format.
        category_id(int): The id of the category to return.
    """
    if(category_id and item_id):
        session = dbconnect()
        try:
            category = session.query(Category).filter_by(id=category_id).one()
            item = session.query(Item).filter_by(id=item_id,
                                                 category_id=category.id).one()
        except NoResultFound:
            session.close()
            flash("JSON error:The item '%s' does not exist for catergory '%s'."
                  % (item_id, category_id))
            return redirect(url_for('showCatalogHome'))
        session.close()
        return jsonify(Item=item.serialise)
    else:
        flash("JSON error: There is no item '%s' for catergory '%s'."
              % (item_id, category_id))
        return redirect(url_for('showCatalogHome'))


# Return JSON of all users
@app.route('/catalog/users/JSON')
def userJSON():
    session = dbconnect()
    users = session.query(User).all()
    session.close()
    return jsonify(users=[i.serialise for i in users])


# Return JSON of all items for a specific user
@app.route('/catalog/user/<user_id>/items/JSON')
def userCatergoryJSON(user_id):
    session = dbconnect()
    items = session.query(Item).filter_by(user_id=user_id).all()
    session.close()
    return jsonify(items=[i.serialise for i in items])
