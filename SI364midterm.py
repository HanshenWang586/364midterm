## SI 364 - Winter 2018
## Mideterm
# Hanshen Wang
# 40602121
# Mar 9

# This is an app where users can post and view thier tips on feeding a certain dog breed. They can also view pictures of the breed by searching the breed name.

###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
import requests
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_script import Shell, Manager
from flask_wtf import FlaskForm
import simplejson as json
from wtforms import StringField, SubmitField, ValidationError # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length # Here, too
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

## App setup code
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.config['SECRET_KEY'] = 'hanshensscretepassword'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/dogTips"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## All app.config values


## Statements for db setup (and manager setup if using Manager)
manager = Manager(app)
db = SQLAlchemy(app)


######################################
######## HELPER FXNS (If any) ########
######################################


##################
##### MODELS #####
##################

class Tip(db.Model):
    __tablename__ = "tips"
    ID = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.String(256))
    title = db.Column(db.String(64))
    breed_id = db.Column(db.Integer, db.ForeignKey('breed.ID'))

    def __repr__(self):
        return "{Tip %r} (ID: {%a})".format(self.content, self.ID)

class Breed(db.Model):
    __tablename__ = "breed"
    ID = db.Column(db.Integer,primary_key=True)
    breedName = db.Column(db.String(64))
    
    def __repr__(self):
        return "{breedName %r} | ID: {%a})".format(self.breedName, self.ID)

class Name(db.Model):
    __tablename__ = "name"
    ID = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64))
    
    def __repr__(self):
        return "{username %r} | ID: {%a})".format(self.username, self.ID)   

###################
###### FORMS ######
###################

def validate_title(form,field):
    title = str(field.data)
    # .contains(,'$','%','#','*')
    if '@' in title:
        raise ValidationError("Title must not contain @$%#*")

class TipForm(FlaskForm):
    username = StringField('Enter your name:', validators=[Required(),Length(1,280)])
    breed = StringField('Enter the breed of your dog:', validators=[Required(),Length(1,280)])
    title = StringField('Enter the title of your tip(no "@$%#*"):', validators=[Required(),Length(1,64),validate_title])
    content = StringField('Enter your tip here: (min 10 characters & max 1000 characters):', validators=[Required(),Length(10,1000)])
    submit = SubmitField('Submit')
 
#######################
###### VIEW FXNS ######
#######################

@app.route('/')
def index():
    form = TipForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    num_tips = len(Tip.query.all())
    return render_template('index.html',form=form)

@app.route('/addTip', methods=['GET', 'POST'])
def addTip():
    form = TipForm(request.form)    
    if form.validate_on_submit():
        breed = form.breed.data
        title = form.title.data
        content = form.content.data
        username = form.username.data
        b = Breed.query.filter_by(breedName=breed).first()
        if b:
            print("Breed exists")
        else:
            b = Breed(breedName=breed)
            db.session.add(b)
            db.session.commit()
        
        n = Name.query.filter_by(username=username).first()
        
        if n:
            print ("Name exists")
        else:
            n = Name(username=username)
            db.session.add(n)
            db.session.commit()

        t = Tip.query.filter_by(title=title,breed_id=b.ID).first()
        if t:
            print("Tip exsits")
            return redirect(url_for('see_all_tips'))
        else:
            t = Tip(title=title,content=content,breed_id=b.ID)
            db.session.add(t)
            db.session.commit()
            response = requests.get("https://dog.ceo/api/breed/" + breed + "/images")
            results = json.loads(response.text)
            if results['status'] == 'success':
                image = results['message'][0]
                return render_template("success.html", tip = content, breed = breed, image = image)
            else: 
                flash("Please enter a valid dog breed!")
    
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    num_tips = len(Tip.query.all())
    
    return render_template("index.html", form = form)

@app.route('/all_names')
def see_all_names():
    names = Name.query.all()
    return render_template('all_names.html',names=names)

@app.route('/all_tips')
def see_all_tips():
    tips = Tip.query.all()
    breed = [(t, Breed.query.filter_by(ID=t.ID).first()) for t in tips]
    return render_template('all_tips.html', tips=breed)

@app.route('/all_breeds')
def see_all_breeds():
    breeds = Breed.query.all()    
    return render_template('all_breeds.html', breeds=breeds)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


## Code to run the application...
if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    manager.run()    
    app.run()

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
