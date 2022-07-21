import functools
from pickle import GET

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

'''This is a blueprint to deal with authentication on the app. A Blueprint is a way to group together related views 
and other code views are how ur app handles incoming requests''' 

#here we are creating a blue print named 'auth', giving it the context (__name__) and adding a url prefix so all URLs
#associated with it will have /auth in them 
bp = Blueprint('auth',__name__,url_prefix='/auth')

@bp.route('/register', methods=('POST','GET'))
def register():
    if request.method =='POST':
        #the request form will have dict mappings of k,v pairs, so here we are pulling those for username and passowrd 
        username = request.form['username']
        password = request.form['password']

        #establish db connection
        db = get_db()
        error = None

        if not username:
            error = 'Username is required'

        elif not password:
            error = 'Password is required' 

        if error is None:
            try:
                #executing a db INSERT statement if there is no error....(?,?) is the syntax to put variables into the statement
                #remember to hash your password when u store them! never safe to store the values as is 
                db.execute(
                    "INSERT into user (username,password) VALUES (?,?)",(username,generate_password_hash(password)),
                )
                db.commit()
            #we could receive an 'IntegrityError' meaning that the username is already in the db 
            except db.IntegrityError:
                error = f"{username} is already registered"
        
        #this will redirecct them to the login page,, using 'url_for' so we don't have the hardcode the url here (best practice)
        else:
            return redirect(url_for('/auth.login'))
    
        #stores messages that can be received during template rendering (so we would show them the error message)
        flash(error)

    #this is the HTML template people will see when they go to /auth/register URL 
    return render_template('/auth/register.html')



@bp.route('/login',methods=('GET','POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        #here we are executing db statement to pull info on the user. fetchone() returns one row from the query ..fetchall() would return a list 
        #if the query returned no results, fetchone would return 'None'
        user = db.execute(
            "SELECT * FROM user WHERE username = ?",
            (username,),).fetchone()
        
        if user is None:
            error = "Incorrect Username"
        
        #here we check the password that the user obj has vs the password given - this hashes the new password given
        #so it can be compared against the password in the db 
        elif not check_password_hash(user['password'],password):
            error = "Incorrect Password"
        
        #session is a dict that stores data across access requests 
        #the data is stored in a cookie that is sent to the browser, so when ur id is stored in a session it will be available 
        #in other requests (i.e. dont have to login on every page)
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    '''This func is run before every view func to check if the user is logged in '''
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id=?", (user_id,),
        ).fetchone()

#create logout page 
@bp.route('/logout')
def logout():
    #here we need to clear session so the id does not continue to load in the load_logged_in_user func
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    '''function creates a wrapper that can be used to wrap views and make sure somebody is logged in to use them. 
    If they are already logged in this just invokes the view as is'''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            #if not loggedin, redirect to login page 
            #when you use Blueprints, the name of the blueprint prepends the name of the function for url_for() call like below
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

    






        
