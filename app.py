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

	# get all the current job profit centres
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

# client database
@app.route('/clientdb', methods=['GET', 'POST'])
def clientdb():

	# get all the current job profit centres
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

	# get all the current job belong entries
	all_jg = db.child("jlg_main").child('jlg_jobbelong').get()
	all_job_belong = []

	try:
		for item in all_jg.each():
			all_job_belong.append(item.val())
	except:
		print("Empty Job Belong Database")

	if request.method == 'POST' and 'clientName' in request.form and 'jobBelong' in request.form and 'jobOwn' in request.form and 'jobProfit' in request.form and 'clientAddress1' in request.form and 'clientAddress2' in request.form and 'clientAddress3' in request.form and 'gstin' in request.form:
		db.child("jlg_main").child("jlg_clients")
		data = {'clientName' : request.form['clientName'], 'jobBelong' : request.form['jobBelong'], 'jobOwn' : request.form['jobOwn'], 'jobProfit' : request.form['jobProfit'], 'clientAddress1' : request.form['clientAddress1'], 'clientAddress2' : request.form['clientAddress2'], 'clientAddress3' : request.form['clientAddress3'], 'gstin' : request.form['gstin']}
		db.push(data)

		return render_template('index.html')

	# get all the current client entries
	all_jc = db.child("jlg_main").child('jlg_clients').get()
	all_job_clients = []

	try:
		for item in all_jc.each():
			all_job_clients.append(item.val())
	except:
		print("Empty Client Database")


	return render_template('client.html', allClients=all_job_clients, allJobs=all_job_owners, jobProfits=all_job_profits, jobBelongs=all_job_belong)


app.secret_key = "jlg-ops"

if __name__ == '__main__':
	app.run(debug=True)