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
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_script import Shell, Manager
from flask_wtf import FlaskForm
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
    content = db.Column(db.String(64))
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



###################
###### FORMS ######
###################

# def validate_username(form,field):
#     if str(field.data)[0] == '@':
#         raise ValidationError("Error:User name must not start with an '@'")

# def validate_displayName(form,field):
#     if str(field.data).count(' ') < 1 or str(field.data) == ' ':
#         raise ValidationError("Error: Display Name must be at least two words") 

class TipForm(FlaskForm):
    breed = StringField('Enter the breed of your dog:', validators=[Required(),Length(1,280)])
    title = StringField('Enter the title of your tip(no "@$%#*"):', validators=[Required(),Length(1,64)])
    content = StringField('Enter your tip here: (min 100 characters & max 1000 characters):', validators=[Required(),Length(100,1000)])
    submit = SubmitField('Submit')
 
#######################
###### VIEW FXNS ######
#######################

@app.route('/')
def index():
    form = TipForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    num_tips = len(Tip.query.all())
    # if form.validate_on_submit():
    #     breed = form.breed.data
    #     title = form.title.data
    #     content = form.content.data
    #     db.session.add(newname)
    #     db.session.commit()
    #     return redirect(url_for('all_names'))
    return render_template('index.html',form=form)

@app.route('/addTip', methods=['GET', 'POST'])
def addTip():
    form = TipForm(request.form)    
    if form.validate_on_submit():
        breed = form.breed.data
        title = form.title.data
        content = form.content.data
        b = Breed.query.filter_by(breedName=breed).first()
        if b:
            print("Breed exists")
        else:
            b = Breed(breedName=breed)
            db.session.add(b)
            db.session.commit()

        t = Tip.query.filter_by(content=content,breeed_id=b.ID).first()
        if t:
            print("Tip exsits")
            return redirect(url_for('see_all_tips'))
        else:
            t = Tweet(content=content,breed_id=b.ID)
            db.session.add(t)
            db.session.commit()
            return redirect(url_for('index'))
    
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    num_tweets = len(Tip.query.all())
    
    return render_template("index.html", form = form)

@app.route('/names')
def all_names():
    # names = Name.query.all()
    return render_template('index.html',names=names)

@app.route('/all_tips')
def see_all_tips():
    # tips = Tip.query.all()
    Breed = [(b, Breed.query.filter_by(ID=b.id).first()) for b in breeds]
    return render_template('all_tips.html', tweets=users)

@app.route('/all_breeds')
def see_all_breeds():
    response = requests.get('https://dog.ceo/api/breeds/list/all')
    return response.text

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
