from flask import Flask, render_template, request, send_file, flash, redirect, session, abort
import pyrebase

app = Flask(__name__)

config = {
  "apiKey": "AIzaSyDtnnxWWrjydXpBdPckxIPDXigBSLEVQsA",
  "authDomain": "jlg-ops.firebaseapp.com",
  "databaseURL": "https://jlg-ops.firebaseio.com",
  "storageBucket": "jlg-ops.appspot.com",
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

# home page
@app.route('/', methods=['GET', 'POST'])
def index():
	return render_template('index.html')

# job profit database
@app.route('/jobprofitdb', methods=['GET', 'POST'])
def jobprofitdb():

	# get all the current job profit entries
	all_jp = db.child("jlg_main").child('jlg_jobprofit').get()
	all_job_profits = []

	try:
		for item in all_jp.each():
			all_job_profits.append(item.val()['jobName'])
	except:
		print("Empty Job Profit Database")

	if request.method == 'POST' and 'jobProfitEntry' in request.form:
		db.child("jlg_main").child("jlg_jobprofit")
		data = {"jobName" : request.form['jobProfitEntry']}
		db.push(data)

		return render_template('index.html')

	return render_template('jobprofit.html', allJobs=all_job_profits)

# job belonging database
@app.route('/jobbelongdb', methods=['GET', 'POST'])
def jobbelongdb():

	# get all the current job belonging entries
	all_jb = db.child("jlg_main").child('jlg_jobbelong').get()
	all_job_belong = []

	try:
		for item in all_jb.each():
			all_job_belong.append(item.val()['compName'])
	except:
		print("Empty Job Belonging Database")

	if request.method == 'POST' and 'jobBelongEntry' in request.form:
		db.child("jlg_main").child("jlg_jobbelong")
		data = {"compName" : request.form['jobBelongEntry']}
		db.push(data)

		return render_template('index.html')

	return render_template('jobbelong.html', allJobs=all_job_belong)

# job owner database
@app.route('/jobownerdb', methods=['GET', 'POST'])
def jobownerdb():

	all_jb = db.child("jlg_main").child('jlg_jobprofit').get()
	all_job_profits = []

	try:
		for item in all_jb.each():
			all_job_profits.append(item.val()['jobName'])
	except:
		print("Empty Job Profits Database")

	# get all the current job owner entries
	all_jo = db.child("jlg_main").child('jlg_jobowner').get()
	all_job_owners = []

	try:
		for item in all_jo.each():
			all_job_owners.append(item.val())
	except:
		print("Empty Job Owner Database")

	if request.method == 'POST' and 'jobOwner' in request.form and 'jobProfitCentre' in request.form:
		db.child("jlg_main").child("jlg_jobowner")
		data = {request.form['jobOwner'] : request.form['jobProfitCentre']}
		db.push(data)

		return render_template('index.html')

	return render_template('jobowner.html', allJobs=all_job_owners, jobProfits=all_job_profits)

app.secret_key = "jlg-ops"

if __name__ == '__main__':
	app.run(debug=True)