import os
import shutil
import csv
import pandas as pd
import sys
from flask import Flask,render_template, url_for, flash, redirect, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, IntegerField, SubmitField, DateField, FloatField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta
import time
import random
import utils


ALLOWED_EXTENSIONS = ['csv']
app = Flask(__name__)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)


# Configurations
app.config['SECRET_KEY'] = '1001778271'
# File Save Place
app.config['UPLOADED_FILES_DEST'] = os.path.join(os.getcwd(), 'FilePlace')
# SQLITE Save Place
app.config['SQL_PLACE'] = os.path.join(os.getcwd(), 'DataBase')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+app.config['SQL_PLACE']+'/assignment2.db'
print(app.config['SQLALCHEMY_DATABASE_URI'])


files = UploadSet('files', ALLOWED_EXTENSIONS, default_dest=app.config['UPLOADED_FILES_DEST'])
configure_uploads(app, files)
# set maximum file size, default is 16MB
patch_request_class(app)  

class SQLEntity(db.Model):
	time = db.Column(db.DateTime, nullable=True)
	latitude = db.Column(db.Float, nullable=True)
	longitude = db.Column(db.Float, nullable=True)
	depth = db.Column(db.Float, nullable=True)
	mag = db.Column(db.Float, nullable=True)
	magType = db.Column(db.Text, nullable=True)
	nst = db.Column(db.Integer, nullable=True)
	gap = db.Column(db.Float, nullable=True)
	dmin = db.Column(db.Float, nullable=True)
	rms = db.Column(db.Float, nullable=True)
	net = db.Column(db.Text, nullable=True)
	id = db.Column(db.Text, nullable=False, primary_key=True)
	updated = db.Column(db.DateTime, nullable=True)
	place = db.Column(db.Text, nullable=True)
	type = db.Column(db.Text, nullable=True)
	horizontalError = db.Column(db.Float, nullable=True)
	depthError = db.Column(db.Float, nullable=True)
	magError = db.Column(db.Float, nullable=True)
	magNst = db.Column(db.Integer, nullable=True)
	status = db.Column(db.Text, nullable=True)
	locationSource = db.Column(db.Text, nullable=True)
	magSource = db.Column(db.Text, nullable=True)



class HomeForm(FlaskForm):
	file = FileField(validators=[
		FileAllowed(files, u'Only can upload csv files')
		])
	submit = SubmitField('Submit')

class MagForm(FlaskForm):
	min_mag = IntegerField("Plz input range min_mag")
	max_mag = IntegerField("Plz input range max_mag")
	submit = SubmitField('Submit')

class Mag1Form(FlaskForm):
	min_mag = IntegerField("Plz input range min_mag")
	max_mag = IntegerField("Plz input range max_mag")
	submit = SubmitField('Submit')



class DateCheckForm(FlaskForm):
	submit = SubmitField('Submit')




# ROUTES!
@app.route('/',methods=['GET','POST'])
def index():
	form = HomeForm()
	if form.validate_on_submit():
		if form.file.data:
			filename = files.save(form.file.data)
			utils.save_csv_tosql(filename, SQLEntity, db)
		return render_template('index.html', form=form)
	return render_template('index.html', form=form)

@app.route('/question1',methods=['GET','POST'])
def question1():
	title = 'show the number of quakes for magnitude below 1, 1 to 2,' \
	        '2 to 3, up to magnitude 5.Show a Pie Chart with each ' \
	        'pie slice in a different color, with labels (totals) outside each pie slice'
	form = MagForm()
	if form.validate_on_submit():
		min_mag = form.min_mag.data
		max_mag = form.max_mag.data
		labels = []
		data = []
		for i in range(min_mag, max_mag):
			labels.append("{}-{} mag level".format(i, i+1))
			results = SQLEntity.query.filter(
				(SQLEntity.mag > i)&
				(SQLEntity.mag < i+1)
			).all()
			data.append(len(results))
		viz = utils.get_viz('pie', labels, data)
		return render_template('question1.html', title=title, form=form, viz=viz.render_embed(),
		                       host=viz.js_host,
		                       script_list=viz.js_dependencies.items
		                       )
	return render_template('question1.html', title=title, form=form)

@app.route('/question2',methods=['GET','POST'])
def question2():
	title = 'show the number of quakes for magnitude below 1, 1 to 2,' \
	        '2 to 3, up to magnitude 5.Show a Bar Chart'
	form = Mag1Form()
	if form.validate_on_submit():
		min_mag = form.min_mag.data
		max_mag = form.max_mag.data
		labels = []
		data = []
		for i in range(min_mag, max_mag):
			labels.append("{}-{} mag level".format(i, i+1))
			results = SQLEntity.query.filter(
				(SQLEntity.mag > i)&
				(SQLEntity.mag < i+1)
			).all()
			data.append(len(results))
		viz = utils.get_viz('bar', labels, data)
		return render_template('question2.html', title=title, form=form, viz=viz.render_embed(),
		                       host=viz.js_host,
		                       script_list=viz.js_dependencies.items
		                       )
	return render_template('question2.html', title=title, form=form)



@app.route('/question3',methods=['GET','POST'])
def question3():
	title = 'What would a graph of magnitude against depth for the 100 recent quakes look like?'
	form = DateCheckForm()
	if form.validate_on_submit():
		results = SQLEntity.query.order_by(SQLEntity.time.desc()).limit(100).all()
		viz = utils.get_sca(results)

		return render_template('question3.html', title=title, form=form, viz=viz.render_embed(),
		                       host=viz.js_host,
		                       script_list=viz.js_dependencies.items
		                       )
	return render_template('question3.html', title=title, form=form)







@app.route('/help')
def help():
	text_list = []
	# Python Version
	text_list.append({
		'label':'Python Version',
		'value':str(sys.version)})
	# os.path.abspath(os.path.dirname(__file__))
	text_list.append({
		'label':'os.path.abspath(os.path.dirname(__file__))',
		'value':str(os.path.abspath(os.path.dirname(__file__)))
		})
	# OS Current Working Directory
	text_list.append({
		'label':'OS CWD',
		'value':str(os.getcwd())})
	# OS CWD Contents
	label = 'OS CWD Contents'
	value = ''
	text_list.append({
		'label':label,
		'value':value})
	return render_template('help.html', text_list=text_list, title='help')

@app.errorhandler(404)
@app.route("/error404")
def page_not_found(error):
	return render_template('404.html',title='404')

@app.errorhandler(500)
@app.route("/error500")
def requests_error(error):
	return render_template('500.html',title='500')

db.create_all()
# port = int(os.getenv('PORT', '5656'))
# app.run(host='0.0.0.0', port=port)