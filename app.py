from flask import Flask, render_template, request, send_file, flash, redirect, session, abort
import pyrebase

from datetime import datetime
from pytz import timezone

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

# index page for exec
@app.route('/exec', methods=['GET', 'POST'])
def execIndex():
	checkDataConsistency()

	# get all the current client entries
	all_je = db.child("jlg_main").child('jlg_execution').get()
	all_job_exec = []

	try:
		for item in all_je.each():
			all_job_exec.append(item.val())
	except:
		print("Empty Execution Database")

	return render_template('execIndex.html', allExec=all_job_exec)


def checkDataConsistency():
	all_je = db.child("jlg_main").child('jlg_execution').get()

	payload = []

	try:
		for item in all_je.each():

			if item.val()['bondready'] != '' and item.val()['dobill'] != '' and item.val()['doready'] != '':
				db.child("jlg_main").child('jlg_execution').child(item.key()).update({'shipping1over': 'yes'})

			if item.val()['befilled'] != '' and item.val()['bereleased'] != '' and item.val()['dutypaid'] != '':
				db.child("jlg_main").child('jlg_execution').child(item.key()).update({'customover': 'yes'})

			if item.val()['cfsover'] != '' and item.val()['cargorel'] != '':
				db.child("jlg_main").child('jlg_execution').child(item.key()).update({'dockover': 'yes'})

			if item.val()['cargotruck'] != '' and item.val()['delvclient'] != '':
				db.child("jlg_main").child('jlg_execution').child(item.key()).update({'delvover': 'yes'})

			if item.val()['slotextn'] != '' and item.val()['emptydep'] != '':
				db.child("jlg_main").child('jlg_execution').child(item.key()).update({'shipping2over': 'yes'})

			# final one
			if item.val()['shipping1over'] == 'yes' and item.val()['customover'] == 'yes' and item.val()['dockover'] == 'yes' and item.val()['delvover'] == 'yes' and item.val()['shipping2over'] == 'yes':
				db.child("jlg_main").child('jlg_execution').child(item.key()).update({'jobComplete': 'yes'})

			payload.append(item.val())

	except Exception as e:
		print(e)
		print("Empty Execution Database")


# update API (restricted use)
@app.route('/updateAPI/<objectId>/<attributeId>', methods=['GET', 'POST'])
def updateAPI(objectId, attributeId):

	timeData = str(datetime.now(timezone('Asia/Kolkata')))[:-16]
	db.child("jlg_main").child('jlg_execution').child(objectId).update({attributeId: timeData})

	return render_template('index.html')

# open jobs page for exec
@app.route('/exec/open', methods=['GET', 'POST'])
def execFilterOpen():

	# get all the current client entries
	all_je = db.child("jlg_main").child('jlg_execution').get()
	all_job_exec_key = []
	all_job_exec_val = []

	try:
		for item in all_je.each():
			if(item.val()['jobComplete'] == 'no'):
				all_job_exec_key.append(item.key())
				all_job_exec_val.append(item.val())
	except Exception as e:
		print(e)
		print("Empty Execution Database")

	print(all_job_exec_key)

	return render_template('execData.html', allExec=all_job_exec_val, myKeys=all_job_exec_key, what='Open')

# closed jobs page for exec
@app.route('/exec/closed', methods=['GET', 'POST'])
def execFilterClosed():

	# get all the current client entries
	all_je = db.child("jlg_main").child('jlg_execution').get()
	all_job_exec_key = []
	all_job_exec_val = []

	try:
		for item in all_je.each():
			if(item.val()['jobComplete'] == 'yes'):
				all_job_exec_key.append(item.key())
				all_job_exec_val.append(item.val())
	except Exception as e:
		print(e)
		print("Empty Execution Database")

	print(all_job_exec_key)

	return render_template('execData.html', allExec=all_job_exec_val, myKeys=all_job_exec_key, what='Closed')

# execution database API (don't use - only for mass data push)
@app.route('/execstatusdb', methods=['GET', 'POST'])
def execstatusdb():

	############################## prefetch data #############################################

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

	############################## prefetch data end #############################################

	if request.method == 'POST':
		db.child("jlg_main").child("jlg_execution")

		jobDone = 'no'
		if(request.form['shipping1over'] == 'yes' and request.form['customover'] == 'yes' and request.form['dockover'] == 'yes' and request.form['delvover'] == 'yes' and request.form['shipping2over'] == 'yes'):
			jobDone = 'yes'

		data = {'jobno1' : request.form['jobno1'], 'jobno2' : request.form['jobno2'], 'jobopen' : request.form['jobopen'], 'clientname' : request.form['clientname'], 'bondready' : request.form['bondready'], 'dobill' : request.form['dobill'], 'doready' : request.form['doready'], 'shipping1over' : request.form['shipping1over'], 'befilled' : request.form['befilled'], 'bereleased' : request.form['bereleased'], 'dutypaid' : request.form['dutypaid'], 'customover' : request.form['customover'], 'cfsover' : request.form['cfsover'], 'cargorel' : request.form['cargorel'], 'dockover' : request.form['dockover'], 'cargotruck' : request.form['cargotruck'], 'delvclient' : request.form['delvclient'], 'delvover' : request.form['delvover'], 'slotextn' : request.form['slotextn'], 'emptydep' : request.form['emptydep'], 'shipping2over' : request.form['shipping2over'], 'jobComplete' : jobDone}
		db.push(data)
		print('push complete')

		return render_template('index.html')

	# get all the current client entries
	all_je = db.child("jlg_main").child('jlg_execution').get()
	all_job_exec = []

	try:
		for item in all_je.each():
			all_job_exec.append(item.val())
	except:
		print("Empty Execution Database")


	return render_template('execution.html', allExec=all_job_exec, allJobs=all_job_owners, jobProfits=all_job_profits, jobBelongs=all_job_belong)


app.secret_key = "jlg-ops"

if __name__ == '__main__':
	app.run(debug=True)