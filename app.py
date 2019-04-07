from flask import Flask, render_template, request, send_file, flash, redirect, session, abort, url_for
import pyrebase

import time
from datetime import datetime
import datetime
from pytz import timezone

from emailSender import sendReportMail

app = Flask(__name__)

config = {
  "apiKey": "AIzaSyApPe5g7BlYVZshE00PXKGcI5ldzVjbj7g",
  "authDomain": "aops-cf59e.firebaseapp.com",
  "databaseURL": "https://aops-cf59e.firebaseio.com",
  "storageBucket": "aops-cf59e.appspot.com",
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

currentDomain = 'https://aops--spotifyrounak.repl.co'

standardEmailHeader = 'ASSLPL Operations Notifications for ' + str(datetime.date.today().strftime('%d-%m-%Y'))
standardEmailContent = 'Summary of recent changes to ' + currentDomain + ':\n'

code2task = {"delFromCFS": "Delivery From CFS", "delToClient": "Delivery to Client", "exportFromSource": "Export From SC", "exportFromTransit": "Export From TC", "importAtIndia": "", "importAtTransit": "Import At TC", "importEstimateAtIndia": "Import ETA At India", "importEstimateAtTransit": "Import ETA at TC", "invoiceDate": "Invoice Date", "invoiceNo": "Invoice Number", "sourceCountry": "Source Country", "transitCountry": "Transit Country", "bill": "Bill of Entry", "chaJobNo": "CHA Job No", "chaname": "CHA Name", "customDutyAmount": "Custom Duty Amount"}

# new UI
@app.route('/newUI')
def newUI():
	return render_template('newIndex.html')


# register route
@app.route('/register', methods=['GET', 'POST'])
def register():

	# first check if user exists or not
	allUsers = db.child("main_db").child("accounts").get()
	try:
		for person in allUsers.each():
			if person.val()['username'] == request.form['username'] or person.val()['email'] == request.form['email']:
				return redirect(url_for('index', note='Account with email/username exists!'))
	except:
		print('Go on!')

	# now register the person
	if request.method == 'POST' and request.form['secretCode'].lower() == 'asslpl2018':
		data = {'email': request.form['email'], 'username': request.form['username'], 'password': request.form['password'], 'admin': 'no'}
		db.child("main_db").child("accounts").push(data)
		return redirect(url_for('index', note='Account creation successful!'))

	return render_template('registerUser.html')


# login route
@app.route('/login', methods=['POST'])
def login():

	userPermissions = []
	# all logins
	logins = db.child("main_db").child('accounts').get()

	try:
		for person in logins.each():
			if person.val()['username'] == request.form['username'] and person.val()['password'] == request.form['password']:

				try:
					userPermissions.append(person.val()['job'])
				except:
					userPermissions.append('null')

				try:
					userPermissions.append(person.val()['overseas'])
				except:
					userPermissions.append('null')

				try:
					userPermissions.append(person.val()['import'])
				except:
					userPermissions.append('null')

				try:
					userPermissions.append(person.val()['destination'])
				except:
					userPermissions.append('null')

				try:
					userPermissions.append(person.val()['bill'])
				except:
					userPermissions.append('null')

				session['userPermissions'] = userPermissions

				session['loggedIn'] = True
				session['guest'] = False
				session['user'] = request.form['username']

				if(person.val()['admin'] == 'yes'):
					session['admin'] = 'yes'
				else:
					session['admin'] = 'no'

				return redirect(url_for('index', note='Login successful!'))
	except Exception as e:
		print(e)
		print("Empty Accounts Database")

	return redirect(url_for('index', note='Invalid credentials!'))


# logout route
@app.route('/logout', methods=['GET', 'POST'])
def logout():
	session['loggedIn'] = False
	session['guest'] = True
	session['user'] = ''
	session['userPermissions'] = []
	session['admin'] = 'no'
	return redirect('/')


# admin API to delete a user
@app.route('/adminAPI/delete/<userId>', methods=['GET', 'POST'])
def deleteUser(userId):
	if(session['admin'] != 'yes'):
		return "no!"

	db.child("main_db").child('accounts').child(userId).remove()
	return redirect('/manageUsers')


# admin API to revoke permissions
@app.route('/adminAPI/cancel/<userId>/<job>', methods=['GET', 'POST'])
def revokeAccess(userId, job):
	if(session['admin'] != 'yes'):
		return "no!"

	db.child("main_db").child('accounts').child(userId).update({job: 'no'})
	return redirect('/manageUsers')


# admin API for updating access level permissions
@app.route('/adminAPI/<userId>/<job>', methods=['GET', 'POST'])
def adminAPI(userId, job):
	if(session['admin'] != 'yes'):
		return "no!"

	db.child("main_db").child('accounts').child(userId).update({job: 'yes'})
	if(job == 'admin'):
		db.child("main_db").child('accounts').child(userId).update({'job': 'yes'})
		db.child("main_db").child('accounts').child(userId).update({'overseas': 'yes'})
		db.child("main_db").child('accounts').child(userId).update({'import': 'yes'})
		db.child("main_db").child('accounts').child(userId).update({'destination': 'yes'})
		db.child("main_db").child('accounts').child(userId).update({'bill': 'yes'})

	return redirect('/manageUsers')


# managing users permission level (index)
@app.route('/manageUsers', methods=['GET', 'POST'])
def manageUsers():

	if(session['admin'] != 'yes'):
		return "no!"

	logins = db.child("main_db").child('accounts').get()
	all_users = []
	all_keys = []

	try:
		for user in logins.each():
			all_users.append(user.val())
			all_keys.append(user.key())
	except:
		print('Accounts DB empty!')

	return render_template('manageUsers.html', allUsers=all_users, myKeys=all_keys, userx=session['user'])


# home page
@app.route('/', methods=['GET', 'POST'])
def index():

	if session.get('user') or session.get('admin'):
		print('Welcome')
	else:
		session['user'] = ''
		session['admin'] = ''
		session['guest'] = True
		session['userPermissions'] = ['no', 'no', 'no', 'no', 'no']

	if(request.args.get('note')):
		whatToSay = request.args.get('note')
	else:
		whatToSay = ''

	if(session.get('loggedIn')):
		return render_template('index.html', loggedIn=session['loggedIn'], user=session['user'], isAdmin=session['admin'], note=whatToSay)
	else:
		return render_template('index.html', loggedIn=False, note=whatToSay)


# job number database
@app.route('/jobnodb', methods=['GET', 'POST'])
def jobno():

	if session['user'] == '':
		return 'Login please'

	if not session['guest'] and session['userPermissions'][0] == 'yes':
		hereAdmin = 'yes'
	else:
		hereAdmin = 'no'

	# get all the job entries
	all_je = db.child("main_db").child('execution').get()
	all_job_exec = []

	try:
		for item in all_je.each():
			all_job_exec.append(item.val())
	except:
		print("Empty Execution Database")

	return render_template('jobIndex.html', userx=session['user'], allExec=all_job_exec, hereAdmin=hereAdmin)


# new job entry
@app.route('/jobnodb/new', methods=['GET', 'POST'])
def newjob():

	if session['loggedIn'] and session['userPermissions'][0] == 'yes':
		hereAdmin = 'yes'
	else:
		hereAdmin = 'no'
		return redirect('/')

	############################## prefetch data #############################################

	# get all the current client entries
	all_jc = db.child("main_db").child('all_clients').get()
	all_job_clients = []

	try:
		for item in all_jc.each():
			all_job_clients.append(item.val())
	except:
		print("Empty Client Database")

	# get all the current country centres
	all_jc = db.child("main_db").child('countrydb').get()
	all_country = []

	try:
		for item in all_jc.each():
			all_country.append(item.val()['countryName'])
	except:
		print("Empty Country Database")

	# get all the current vendor entries
	all_jv = db.child("main_db").child('vendordb').get()
	all_vendor = []

	try:
		for item in all_jv.each():
			all_vendor.append(item.val())
	except:
		print("Empty Vendor Database")

	############################## prefetch data end #############################################

	if request.method == 'POST':
		db.child("main_db").child("execution")
		data = {'jobType': request.form['jobType'], 'jobno1': request.form['jobno1'], 'jobopen': request.form['jobopen'], 'clientname': request.form['clientxname'], 'clientOf': request.form['clientOf'], 'sourceCountry': '', 'transitCountry': '', 'chaname': '', 'packageq': request.form['packageq'], 'commodity': request.form['commodity'], 'exportFromSource' : '', 'importEstimateAtTransit' : '', 'importAtTransit' : '',  'exportFromTransit' : '', 'importEstimateAtIndia' : '', 'importAtIndia' : '', 'chaJobNo' : '', 'bill' : '', 'customDutyAmount' : '', 'delFromCFS' : '', 'delToClient' : '', 'jobCloseDate' : '', 'invoiceNo' : '', 'invoiceDate' : '', 'jobComplete' : 'no'}
		db.push(data)

		try:
			sendReportMail(standardEmailHeader, standardEmailContent + 'New Job Addition by ' + session['user'] + ' : ' + request.form['jobno1'] + request.form['clientname'])
		except:
			pass

		return redirect('/')

	return render_template('newJob.html', allClients=all_job_clients, allCountries=all_country, allVendors=all_vendor, userx=session['user'])


# admin API to delete a profitDB entry
@app.route('/adminAPI/delete/profit/<entry>', methods=['GET', 'POST'])
def deleteProfit(entry):
	if(session['admin'] != 'yes'):
		return "no!"

	db.child("main_db").child('jobprofit').child(entry).remove()
	return redirect('/')


# job profit database
@app.route('/jobprofitdb', methods=['GET', 'POST'])
def jobprofitdb():

	if not session['guest'] and session['userPermissions'][0] == 'yes':
		hereAdmin = 'yes'
	else:
		hereAdmin = 'no'

	# get all the current job profit entries
	all_jp = db.child("main_db").child('jobprofit').get()
	all_job_profits = []
	all_job_profits_keys = []

	try:
		for item in all_jp.each():
			all_job_profits_keys.append(item.key())
			all_job_profits.append(item.val()['jobName'])
	except:
		print("Empty Job Profit Database")

	if request.method == 'POST' and 'jobProfitEntry' in request.form:
		db.child("main_db").child("jobprofit")
		data = {"jobName" : request.form['jobProfitEntry']}
		db.push(data)

		return redirect('/')

	return render_template('jobprofit.html', hereAdmin=hereAdmin, allJobs=all_job_profits, allJobsKeys=all_job_profits_keys)


# job belonging database
@app.route('/jobbelongdb', methods=['GET', 'POST'])
def jobbelongdb():

	if session['user'] == '':
		return 'Login please'

	if session['admin'] == 'yes':
		hereAdmin = 'yes'
	else:
		hereAdmin = 'no'

	# get all the current job belonging entries
	all_jb = db.child("main_db").child('jobbelong').get()
	all_job_belong = []

	try:
		for item in all_jb.each():
			all_job_belong.append(item.val()['compName'])
	except:
		print("Empty Job Belonging Database")

	if request.method == 'POST' and 'jobBelongEntry' in request.form:
		db.child("main_db").child("jobbelong")
		data = {"compName" : request.form['jobBelongEntry']}
		db.push(data)

		try:
			sendReportMail(standardEmailHeader, standardEmailContent + 'New Job Owner Addition by ' + session['user'] + ' : ' + request.form['jobBelongEntry'])
		except:
			pass
		return redirect('/')

	return render_template('jobbelong.html', hereAdmin=hereAdmin, allJobs=all_job_belong, userx=session['user'])


# vendor database
@app.route('/vendordb', methods=['GET', 'POST'])
def vendordb():

	if session['user'] == '':
		return 'Login please'

	if session['admin'] == 'yes':
		hereAdmin = 'yes'
	else:
		hereAdmin = 'no'

	# get all the current job belonging entries
	all_vendor = db.child("main_db").child('vendordb').get()
	all_vendor_collected = []

	try:
		for item in all_vendor.each():
			all_vendor_collected.append(item.val())
	except:
		print("Empty Vendor Database")

	if request.method == 'POST' and 'vendorName' in request.form and 'vendorService' in request.form:
		db.child("main_db").child("vendordb")
		data = {"vendorName" : request.form['vendorName'], "vendorService" : request.form['vendorService']}
		db.push(data)

		try:
			sendReportMail(standardEmailHeader, standardEmailContent + 'New Job Vendor Addition by ' + session['user'] + ' : ' + request.form['vendorName'] + request.form['vendorService'])
		except:
			pass
		return redirect('/')

	return render_template('vendordb.html', hereAdmin=hereAdmin, allJobs=all_vendor_collected, userx=session['user'])

# country database
@app.route('/countrydb', methods=['GET', 'POST'])
def countrydb():

	if session['user'] == '':
		return 'Login please'

	if session['admin'] == 'yes':
		hereAdmin = 'yes'
	else:
		hereAdmin = 'no'

	# get all the current job belonging entries
	all_country = db.child("main_db").child('countrydb').get()
	all_country_collected = []

	try:
		for item in all_country.each():
			all_country_collected.append(item.val()['countryName'])
	except:
		print("Empty Vendor Database")

	if request.method == 'POST' and 'countryName' in request.form :
		db.child("main_db").child("countrydb")
		data = {"countryName" : request.form['countryName']}
		db.push(data)

		try:
			sendReportMail(standardEmailHeader, standardEmailContent + 'New Country Addition by ' + session['user'] + ' : ' + request.form['countryName'])
		except:
			pass
		return redirect('/')

	return render_template('countrydb.html', hereAdmin=hereAdmin, allJobs=all_country_collected, userx=session['user'])

# job owner database
@app.route('/jobownerdb', methods=['GET', 'POST'])
def jobownerdb():

	if session['admin'] == 'yes':
		hereAdmin = 'yes'
	else:
		hereAdmin = 'no'

	# get all the current job profit centres
	all_jb = db.child("main_db").child('jobprofit').get()
	all_job_profits = []

	try:
		for item in all_jb.each():
			all_job_profits.append(item.val()['jobName'])
	except:
		print("Empty Job Profits Database")

	# get all the current job owner entries
	all_jo = db.child("main_db").child('jobowner').get()
	all_job_owners = []

	try:
		for item in all_jo.each():
			all_job_owners.append(item.val())
	except:
		print("Empty Job Owner Database")

	if request.method == 'POST' and 'jobOwner' in request.form and 'jobProfitCentre' in request.form:
		db.child("main_db").child("jobowner")
		data = {request.form['jobOwner'] : request.form['jobProfitCentre']}
		db.push(data)

		return redirect('/')

	return render_template('jobowner.html', hereAdmin=hereAdmin, allJobs=all_job_owners, jobProfits=all_job_profits)


# client database view
@app.route('/clientview', methods=['GET', 'POST'])
def clientView():

	if session['user'] == '':
		return 'Login please'

	# get all the current client entries
	all_jc = db.child("main_db").child('all_clients').get()
	all_job_clients = []

	if session['admin'] == 'yes':
		hereAdmin = 'yes'
	else:
		hereAdmin = 'no'

	try:
		for item in all_jc.each():
			all_job_clients.append(item.val())
	except Exception as e:
		print(e)
		print("Empty Client Database")

	return render_template('clientView.html', allClients=all_job_clients, hereAdmin=hereAdmin)


# client database new entry
@app.route('/clientdb', methods=['GET', 'POST'])
def clientdb():

	if session['loggedIn'] and session['userPermissions'][0] == 'yes':
		hereAdmin = 'yes'
	else:
		hereAdmin = 'no'
		return 'no'

	# get all the current job belong entries
	all_jg = db.child("main_db").child('jobbelong').get()
	all_job_belong = []

	try:
		for item in all_jg.each():
			all_job_belong.append(item.val())
	except:
		print("Empty Job Belong Database")

	if request.method == 'POST' and 'clientName' in request.form and 'jobBelong' in request.form and 'clientAddress1' in request.form and 'clientAddress2' in request.form and 'clientAddress3' in request.form and 'gstin' in request.form and 'mobile' in request.form and 'email' in request.form:
		db.child("main_db").child("all_clients")
		data = {'clientname' : request.form['clientName'], 'jobBelong' : request.form['jobBelong'], 'clientAddress1' : request.form['clientAddress1'], 'clientAddress2' : request.form['clientAddress2'], 'clientAddress3' : request.form['clientAddress3'], 'gstin' : request.form['gstin'], 'mobile' : request.form['mobile'], 'email' : request.form['email']}
		db.push(data)

		try:
			sendReportMail(standardEmailHeader, standardEmailContent + 'New Job Client Addition by ' + session['user'] + ' : ' + request.form['clientName'])
		except:
			pass
		return redirect('/')

	# get all the current client entries
	all_jc = db.child("main_db").child('all_clients').get()
	all_job_clients = []

	try:
		for item in all_jc.each():
			all_job_clients.append(item.val())
	except Exception as e:
		print(e)
		print("Empty Client Database")

	return render_template('client.html', allClients=all_job_clients, jobBelongs=all_job_belong, userx=session['user'])


# index page for exec
@app.route('/exec', methods=['GET', 'POST'])
def execIndex():

	if session['user'] == '':
		return 'Login please'

	if session['admin'] == 'yes':
		aright = "yes"
	else:
		aright = "no"

	# get all the current client entries
	all_je = db.child("main_db").child('execution').get()
	all_job_exec = []

	try:
		for item in all_je.each():
			all_job_exec.append(item.val())
	except:
		print("Empty Execution Database")

	return render_template('execIndex.html', admin=aright, user=session['user'], allExec=all_job_exec)


def checkDataConsistency(myId="all"):

	if(myId == "all"):
		print('Entire Database check')
		try:
			all_je = db.child("main_db").child('execution').get()
			for item in all_je.each():
				if item.val() is None:
					continue

				if item.val()['bondready'] != '' and item.val()['dobill'] != '' and item.val()['doready'] != '':
					db.child("main_db").child('execution').child(item.key()).update({'shipping1over': 'yes'})
				else:
					db.child("main_db").child('execution').child(item.key()).update({'shipping1over': 'no'})

				if item.val()['befilled'] != '' and item.val()['bereleased'] != '' and item.val()['dutypaid'] != '':
					db.child("main_db").child('execution').child(item.key()).update({'customover': 'yes'})
				else:
					db.child("main_db").child('execution').child(item.key()).update({'customover': 'no'})

				if item.val()['cfsover'] != '' and item.val()['cargorel'] != '':
					db.child("main_db").child('execution').child(item.key()).update({'dockover': 'yes'})
				else:
					db.child("main_db").child('execution').child(item.key()).update({'dockover': 'no'})

				if item.val()['cargotruck'] != '' and item.val()['delvclient'] != '':
					db.child("main_db").child('execution').child(item.key()).update({'delvover': 'yes'})
				else:
					db.child("main_db").child('execution').child(item.key()).update({'delvover': 'no'})

				if item.val()['slotextn'] != '' and item.val()['emptydep'] != '':
					db.child("main_db").child('execution').child(item.key()).update({'shipping2over': 'yes'})
				else:
					db.child("main_db").child('execution').child(item.key()).update({'shipping2over': 'no'})

				# preclose one
				if item.val()['shipping1over'] == 'yes' and item.val()['customover'] == 'yes' and item.val()['dockover'] == 'yes' and item.val()['delvover'] == 'yes' and item.val()['shipping2over'] == 'yes':
					db.child("main_db").child('execution').child(item.key()).update({'preClose': 'yes'})
					db.child("main_db").child('execution').child(item.key()).update({'jobComplete': 'yes'})

				# if item.val()['preClose'] == 'yes' and item.val()['bill1'] != '' and item.val()['bill2'] != '':
				# 	db.child("main_db").child('execution').child(item.key()).update({'jobComplete': 'yes'})

					if(item.val()['jobCloseDate'] == ''):
						closeDate = str(datetime.now(timezone('Asia/Kolkata')))[:-22]
						closeDate = closeDate.split('-')[2] + '-' + closeDate.split('-')[1] + '-' + closeDate.split('-')[0][-2:]
						db.child("main_db").child('execution').child(item.key()).update({'jobCloseDate': closeDate})

				else:
					db.child("main_db").child('execution').child(item.key()).update({'jobComplete': 'no'})
					db.child("main_db").child('execution').child(item.key()).update({'jobCloseDate': ''})


		except Exception as e:
			print(e)
			print("Empty Execution Database")

		return

	try:
		item = db.child("main_db").child('execution').child(myId).get()
		print('Single item Database check')

		if item.val()['bondready'] != '' and item.val()['dobill'] != '' and item.val()['doready'] != '':
			db.child("main_db").child('execution').child(item.key()).update({'shipping1over': 'yes'})
		else:
			db.child("main_db").child('execution').child(item.key()).update({'shipping1over': 'no'})
		if item.val()['befilled'] != '' and item.val()['bereleased'] != '' and item.val()['dutypaid'] != '':
			db.child("main_db").child('execution').child(item.key()).update({'customover': 'yes'})
		else:
			db.child("main_db").child('execution').child(item.key()).update({'customover': 'no'})
		if item.val()['cfsover'] != '' and item.val()['cargorel'] != '':
			db.child("main_db").child('execution').child(item.key()).update({'dockover': 'yes'})
		else:
			db.child("main_db").child('execution').child(item.key()).update({'dockover': 'no'})
		if item.val()['cargotruck'] != '' and item.val()['delvclient'] != '':
			db.child("main_db").child('execution').child(item.key()).update({'delvover': 'yes'})
		else:
			db.child("main_db").child('execution').child(item.key()).update({'delvover': 'no'})
		if item.val()['slotextn'] != '' and item.val()['emptydep'] != '':
			db.child("main_db").child('execution').child(item.key()).update({'shipping2over': 'yes'})
		else:
			db.child("main_db").child('execution').child(item.key()).update({'shipping2over': 'no'})

		# preclose one
		if item.val()['shipping1over'] == 'yes' and item.val()['customover'] == 'yes' and item.val()['dockover'] == 'yes' and item.val()['delvover'] == 'yes' and item.val()['shipping2over'] == 'yes':
			db.child("main_db").child('execution').child(item.key()).update({'preClose': 'yes'})
			db.child("main_db").child('execution').child(item.key()).update({'jobComplete': 'yes'})

		# if item.val()['preClose'] == 'yes' and item.val()['bill1'] != '' and item.val()['bill2'] != '':
		# 	db.child("main_db").child('execution').child(item.key()).update({'jobComplete': 'yes'})

			if(item.val()['jobCloseDate'] == ''):
				closeDate = str(datetime.now(timezone('Asia/Kolkata')))[:-22]
				closeDate = closeDate.split('-')[2] + '-' + closeDate.split('-')[1] + '-' + closeDate.split('-')[0][-2:]

				db.child("main_db").child('execution').child(item.key()).update({'jobCloseDate': closeDate})
		else:
			db.child("main_db").child('execution').child(item.key()).update({'jobComplete': 'no'})
			db.child("main_db").child('execution').child(item.key()).update({'jobCloseDate': ''})
	except Exception as e:
		print(e)
		print('Updation problem')


# manual data consistency check - beware VERY VERY COSTLY PROCESS
@app.route('/refreshData', methods=['GET', 'POST'])
def refreshDB():
	checkDataConsistency()
	return redirect('/')


# update confirmation
@app.route('/updateConfirmation', methods=['GET', 'POST'])
def confirmUpdate():

	if not session.get('loggedIn'):
		return redirect('/')

	return redirect('/logout')


# update cancellation
@app.route('/updateAPI/cancel/<objectId>/<attributeId>', methods=['GET', 'POST'])
def cancelUpdate(objectId, attributeId):

	if not session.get('loggedIn'):
		return redirect('/')

	db.child("main_db").child('execution').child(objectId).update({attributeId: ""})

	# sleep for 3s because Firebase needs a little time to update
	time.sleep(3)

	# double-check for extra surity
	checkDataConsistency(objectId)
	checkDataConsistency(objectId)

	return redirect('/logout')


# update API (restricted use)
@app.route('/updateAPI/<objectId>/<attributeId>', methods=['GET', 'POST'])
def updateAPI(objectId, attributeId):

	if not session.get('loggedIn'):
		flash('You don’t have permission to execute this action!')
		return redirect(request.referrer)

	closeDate = str(datetime.now(timezone('Asia/Kolkata')))
	timeData = closeDate[:-22].split('-')[2] + '-' + closeDate[:-22].split('-')[1] + '-' + closeDate[:-22].split('-')[0][-2:] + ' ' + closeDate[:-16][-5:] + ' ' + session['user']
	db.child("main_db").child('execution').child(objectId).update({attributeId: timeData})

	# sleep for 3s because Firebase needs a little time to update
	time.sleep(3)

	# double-check for extra surity
	checkDataConsistency(objectId)
	checkDataConsistency(objectId)

	return render_template('confirmSubmit.html', objectId=objectId, attributeId=attributeId)


# update API for the bill updations (on the popup page)
@app.route('/updateAPI/bill/<objectId>/<attributeId>', methods=['GET', 'POST'])
def billUpdateAPI(objectId, attributeId):

	if request.method == 'POST':
		billText = request.form['billText']
		db.child("main_db").child('execution').child(objectId).update({attributeId: billText})
		mainValue = billText
		# sleep for 3s because Firebase needs a little time to update
		#time.sleep(3)
	
		# double-check for extra surity
		#checkDataConsistency(objectId)
		#checkDataConsistency(objectId)

		editLink = currentDomain + '/updateAPI/bill/' + objectId + '/' + attributeId
		print(editLink)
		jobNumber = db.child("main_db").child("execution").child(objectId).child('jobno1').get().val()
		sendReportMail(standardEmailHeader, standardEmailContent + 'There was a recent write to your Execution DB by ' + session['user'] + '.\n Field: ' + code2task[attributeId] + '\n Value: ' + mainValue + '\n Job Number: ' + jobNumber + '\nYou can still edit it here: ' + editLink)
		return 'success'

	return render_template('billPage.html', objectId=objectId, attributeId=attributeId)


# update API for the country updations (on the popup page)
@app.route('/updateAPI/country/<objectId>/<attributeId>', methods=['GET', 'POST'])
def countryUpdateAPI(objectId, attributeId):

	if request.method == 'POST':
		countryDetails = request.form['countryDetails']
		db.child("main_db").child('execution').child(objectId).update({attributeId: countryDetails})
		mainValue = countryDetails

		editLink = currentDomain + '/updateAPI/country/' + objectId + '/' + attributeId
		print(editLink)
		jobNumber = db.child("main_db").child("execution").child(objectId).child('jobno1').get().val()
		sendReportMail(standardEmailHeader, standardEmailContent + 'There was a recent write to your Execution DB by ' + session['user'] + '.\n Field: ' + code2task[attributeId] + '\n Value: ' + mainValue + '\n Job Number: ' + jobNumber + '\nYou can still edit it here: ' + editLink)
		return 'success'

	# get all the current country centres
	all_jc = db.child("main_db").child('countrydb').get()
	all_country = []

	try:
		for item in all_jc.each():
			all_country.append(item.val()['countryName'])
	except:
		print("Empty Country Database")

	return render_template('countryPage.html', objectId=objectId, attributeId=attributeId, allCountries=all_country)


# update API for the CHA updations (on the popup page)
@app.route('/updateAPI/cha/<objectId>/<attributeId>', methods=['GET', 'POST'])
def chaUpdateAPI(objectId, attributeId):

	if request.method == 'POST':
		chaDetails = request.form['chaDetails']
		db.child("main_db").child('execution').child(objectId).update({attributeId: chaDetails})
		mainValue = chaDetails

		editLink = currentDomain + '/updateAPI/cha/' + objectId + '/' + attributeId
		print(editLink)
		jobNumber = db.child("main_db").child("execution").child(objectId).child('jobno1').get().val()
		sendReportMail(standardEmailHeader, standardEmailContent + 'There was a recent write to your Execution DB by ' + session['user'] + '.\n Field: ' + code2task[attributeId] + '\n Value: ' + mainValue + '\n Job Number: ' + jobNumber + '\nYou can still edit it here: ' + editLink)
		return 'success'

	# get all the current country centres
	all_jv = db.child("main_db").child('vendordb').get()
	all_vendor = []

	try:
		for item in all_jv.each():
			all_vendor.append(item.val()['vendorName'])
	except:
		print("Empty Vendor Database")

	if attributeId == 'chaname':
		return render_template('chaName.html', objectId=objectId, attributeId=attributeId, allVendors=all_vendor)
	else:
		return render_template('chaBill.html', objectId=objectId, attributeId=attributeId)


# update API for the invoice updations (on the popup page)
@app.route('/updateAPI/invoice/<objectId>/<attributeId>', methods=['GET', 'POST'])
def invoiceUpdateAPI(objectId, attributeId):

	if request.method == 'POST':
		invoiceDetails = request.form['invoiceDetails']
		db.child("main_db").child('execution').child(objectId).update({attributeId: invoiceDetails})
		mainValue = invoiceDetails

		editLink = currentDomain + '/updateAPI/invoice/' + objectId + '/' + attributeId
		print(editLink)
		jobNumber = db.child("main_db").child("execution").child(objectId).child('jobno1').get().val()
		sendReportMail(standardEmailHeader, standardEmailContent + 'There was a recent write to your Execution DB by ' + session['user'] + '.\n Field: ' + code2task[attributeId] + '\n Value: ' + mainValue + '\n Job Number: ' + jobNumber + '\nYou can still edit it here: ' + editLink)
		return 'success'

	return render_template('invoicePage.html', objectId=objectId, attributeId=attributeId)


# update API for the date updations (on the popup page)
@app.route('/updateAPI/date/<objectId>/<attributeId>', methods=['GET', 'POST'])
def dateUpdateAPI(objectId, attributeId):

	if request.method == 'POST':
		dateDetails = request.form['dateDetails']
		db.child("main_db").child('execution').child(objectId).update({attributeId: dateDetails})
		mainValue = dateDetails
		if attributeId == 'invoiceDate':
			db.child("main_db").child('execution').child(objectId).update({'jobCloseDate': dateDetails})
			db.child("main_db").child('execution').child(objectId).update({'jobComplete': 'yes'})

		editLink = currentDomain + '/updateAPI/date/' + objectId + '/' + attributeId
		print(editLink)
		jobNumber = db.child("main_db").child("execution").child(objectId).child('jobno1').get().val()
		sendReportMail(standardEmailHeader, standardEmailContent + 'There was a recent write to your Execution DB by ' + session['user'] + '.\n Field: ' + code2task[attributeId] + '\n Value: /' + mainValue + '/\n Job Number: ' + jobNumber + '\nYou can still edit it here: ' + editLink)
		return 'success'

	return render_template('datePage.html', objectId=objectId, attributeId=attributeId)


# open jobs page for exec
@app.route('/exec/open', methods=['GET', 'POST'])
def execFilterOpen():

	if session['user'] == '':
		return 'Login please'

	if session['admin'] == 'yes':
		aright = "yes"
	else:
		aright = "no"

	# get all the current client entries
	all_je = db.child("main_db").child('execution').get()
	all_job_exec_key = []
	all_job_exec_val = []

	try:
		for item in all_je.each():

			if item.val() is None:
				continue

			if(item.val()['jobComplete'] == 'no'):
				all_job_exec_key.append(item.key())
				all_job_exec_val.append(item.val())
	except Exception as e:
		print(e)
		print("Empty Execution Database")

	print(session['userPermissions'])

	return render_template('execData.html', admin=aright, user=session['user'], allExec=all_job_exec_val, myKeys=all_job_exec_key, what='Open', permissions=session['userPermissions'])


# closed jobs page for exec
@app.route('/exec/closed', methods=['GET', 'POST'])
def execFilterClosed():

	if session['user'] == '':
		return 'Login please'

	if session['admin'] == 'yes':
		aright = "yes"
	else:
		aright = "no"

	# get all the current client entries
	all_je = db.child("main_db").child('execution').get()
	all_job_exec_key = []
	all_job_exec_val = []

	try:
		for item in all_je.each():

			if item.val() is None:
				continue

			if(item.val()['jobComplete'] == 'yes'):
				all_job_exec_key.append(item.key())
				all_job_exec_val.append(item.val())
	except Exception as e:
		print(e)
		print("Empty Execution Database")

	return render_template('execData.html', admin=aright, user=session['user'], allExec=all_job_exec_val, myKeys=all_job_exec_key, what='Closed', permissions=['yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'])


# execution database API (don't use - only for mass data push)
@app.route('/execstatusdb', methods=['GET', 'POST'])
def execstatusdb():

	if session['admin'] == 'yes':
		aright = "yes"
	else:
		aright = "no"

	############################## prefetch data #############################################

	# get all the current job profit centres
	all_jb = db.child("main_db").child('jobprofit').get()
	all_job_profits = []

	try:
		for item in all_jb.each():
			all_job_profits.append(item.val()['jobName'])
	except:
		print("Empty Job Profits Database")

	# get all the current job owner entries
	all_jo = db.child("main_db").child('jobowner').get()
	all_job_owners = []

	try:
		for item in all_jo.each():
			all_job_owners.append(item.val())
	except:
		print("Empty Job Owner Database")

	# get all the current job belong entries
	all_jg = db.child("main_db").child('jobbelong').get()
	all_job_belong = []

	try:
		for item in all_jg.each():
			all_job_belong.append(item.val())
	except:
		print("Empty Job Belong Database")

	############################## prefetch data end #############################################

	if request.method == 'POST':
		db.child("main_db").child("execution")

		jobDone = 'no'
		if(request.form['shipping1over'] == 'yes' and request.form['customover'] == 'yes' and request.form['dockover'] == 'yes' and request.form['delvover'] == 'yes' and request.form['shipping2over'] == 'yes'):
			jobDone = 'yes'

		data = {'jobno1' : request.form['jobno1'], 'jobno2' : request.form['jobno2'], 'jobopen' : request.form['jobopen'], 'clientname' : request.form['clientname'], 'bondready' : request.form['bondready'], 'dobill' : request.form['dobill'], 'doready' : request.form['doready'], 'shipping1over' : request.form['shipping1over'], 'befilled' : request.form['befilled'], 'bereleased' : request.form['bereleased'], 'dutypaid' : request.form['dutypaid'], 'customover' : request.form['customover'], 'cfsover' : request.form['cfsover'], 'cargorel' : request.form['cargorel'], 'dockover' : request.form['dockover'], 'cargotruck' : request.form['cargotruck'], 'delvclient' : request.form['delvclient'], 'delvover' : request.form['delvover'], 'slotextn' : request.form['slotextn'], 'emptydep' : request.form['emptydep'], 'shipping2over' : request.form['shipping2over'], 'jobComplete' : jobDone}
		db.push(data)
		print('push complete')

		return redirect('/')

	# get all the current client entries
	all_je = db.child("main_db").child('execution').get()
	all_job_exec = []

	try:
		for item in all_je.each():
			all_job_exec.append(item.val())
	except:
		print("Empty Execution Database")


	return render_template('execution.html', admin=aright, allExec=all_job_exec, allJobs=all_job_owners, jobProfits=all_job_profits, jobBelongs=all_job_belong)


# customer error display and reporting page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


app.secret_key = "asslpl-ops"

if __name__ == '__main__':
	app.run(debug=True, threaded=True)