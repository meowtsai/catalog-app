from flask import (
                    Flask,
                    render_template,
                    url_for,
                    request,
                    redirect,
                    flash,
                    jsonify)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from models import Category, Base, Product, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
from google.oauth2 import id_token
from google.auth.transport import requests
import os.path

app = Flask(__name__)

engine = create_engine('sqlite:////var/www/html/catalog-app/categoryproduct.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)

CLIENT_ID = json.loads(
    open('/var/www/html/catalog-app/client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalop Application"

app.secret_key = 'super_secret_key'


@app.teardown_request
def remove_session(ex=None):
    session.remove()


@app.route('/login')
def showLogin():
    # redirect to login page
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=login_session['state'])


@app.route('/gconnect2', methods=['POST'])
def gconnect2():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # if the ID token is properly signed by Google.
    # Use Google's public keys to verify the token's signature.
    token = request.data
    try:
        idinfo = id_token.verify_oauth2_token(token,
                                              requests.Request(),
                                              CLIENT_ID)

        # if the value of iss in the ID token is equal to:
        # accounts.google.com or https://accounts.google.com.
        if idinfo['iss'] not in ['accounts.google.com',
                                 'https://accounts.google.com']:
            response = make_response(json.dumps('Invalid User.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        userid = idinfo['sub']
    except ValueError:
        # Invalid token
        response = make_response(json.dumps('Invalid token.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # if the value of aud in the ID token is equal to your client ID
    # This check prevents ID tokens issued to a malicious app
    # being used to access data about the same user on backend server.
    if idinfo['aud'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = token
    login_session['gplus_id'] = userid

    login_session['username'] = idinfo['name']
    login_session['picture'] = idinfo['picture']
    login_session['email'] = idinfo['email']
    cUserId = getUser(login_session['email'])
    if cUserId is None:
        cUserId = createUser(login_session)

    login_session['user_id'] = cUserId
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    output += ' "-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    flash("you are now logged out.")
    return redirect(url_for('catalog_all'))


# Create a user
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    addedUser = (session.query(User)
                 .filter_by(email=login_session['email'])
                 .one())
    return addedUser.id


def getUser(user_email):
    user = session.query(User).filter_by(email=user_email).first()
    if user is None:
        return None
    else:
        return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user


# JSON APIs to view Catalog Information
@app.route('/catalog/JSON')
def catalogJSON():
    categories = session.query(Category).all()
    return jsonify(CategoryItems=[i.serialize for i in categories])


@app.route('/catalog/<int:catalog_id>/items/JSON')
def itemsByCategoryJSON(catalog_id):
    items = session.query(Product).filter_by(category_id=catalog_id).all()
    return jsonify(items=[r.serialize for r in items])


@app.route('/catalog/<int:catalog_id>/<int:item_id>/JSON')
def itemsByIdJSON(catalog_id, item_id):
    item = session.query(Product).filter_by(id=item_id).first()
    return jsonify(item.serialize)


@app.route('/')
@app.route('/catalog/')
def catalog_all():
    categories = session.query(Category).all()
    items = session.query(Product).all()
    if 'username' not in login_session:
        return render_template('catalog_public.html',
                               categories=categories,
                               items=items)
    else:
        return render_template('catalog.html',
                               categories=categories,
                               items=items,
                               login_session=login_session)


@app.route('/catalog/<int:catalog_id>/items')
def catalogItems(catalog_id):
    categories = session.query(Category).all()
    items = session.query(Product).filter_by(category_id=catalog_id).all()
    return render_template('catalog.html',
                           categories=categories,
                           items=items)


@app.route('/catalog/<int:category_id>/<int:item_id>')
def catalogItemDetail(category_id, item_id):
    """shows specific information of that item."""
    item = session.query(Product).filter_by(id=item_id).one()
    creator = getUserInfo(item.user_id)
    if ('username' not in login_session or
        creator.id != login_session['user_id']):
            return render_template('iteminfo_public.html',
                                   category_id=category_id, item=item)
    else:
        return render_template('iteminfo.html',
                               category_id=category_id,
                               item=item)


@app.route('/catalog/items/new', methods=['GET', 'POST'])
def newCatalogItem():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = Product(name=request.form['name'],
                          description=request.form['description'],
                          category_id=request.form['category'],
                          user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("new product added!")
        return redirect(url_for('catalog_all'))
    else:
        categories = session.query(Category).all()
        return render_template('newitem.html', categories=categories)


@app.route('/catalog/<int:category_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editCatalogItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Product).filter_by(id=item_id).one()
    creator = getUserInfo(editedItem.user_id)
    if creator.id != login_session['user_id']:
        return redirect('/')
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']

        if request.form['description']:
            editedItem.description = request.form['description']

        if request.form['category']:
            editedItem.category_id = request.form['category']

        session.add(editedItem)
        session.commit()
        flash("product %s edited!" % editedItem.name)
        return redirect(url_for('catalogItemDetail',
                        category_id=category_id,
                        item_id=item_id))
    else:
        categories = session.query(Category).all()
        return render_template('edititem.html',
                               category_id=category_id,
                               item=editedItem,
                               categories=categories)


@app.route('/catalog/<int:category_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteCatalogItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    deleteItem = session.query(Product).filter_by(id=item_id).one()
    creator = getUserInfo(deleteItem.user_id)
    if creator.id != login_session['user_id']:
        return redirect('/')
    if request.method == 'POST':
        if deleteItem:
            session.delete(deleteItem)
            session.commit()
            flash("product %s deleted!" % deleteItem.name)
        return redirect(url_for('catalog_all'))
    else:
        return render_template('deleteitem.html',
                               category_id=category_id,
                               item=deleteItem)


if __name__ == '__main__':

    app.debug = True
    app.run(host='0.0.0.0', port=5000)
