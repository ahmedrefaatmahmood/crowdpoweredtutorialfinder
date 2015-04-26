#!/usr/local/bin/python2.9
import flask, random, os
import re
from threading import Lock
from sqlite3 import dbapi2 as sqlite3
#from flask import Flask, request,session,g,redirect,url_for,abort,render_template,flash,json,jsonify
from contextlib import closing
import crowdlib as cl, crowdlib_settings
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
	jsonify,
	session,
	g,
	_app_ctx_stack
)

     
PORT=8006
#PORT=8001
URL_PERFIX='/%02d'%(PORT%100)

# configuration
DATABASE = 'sqlite_db'
DEBUG = False

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
formsubmiturl="https://workersandbox.mturk.com/mturk/externalSubmit"

requester_count=0
worker_count=[0]
voter_count=[0]
task_flag=[0]
lock=Lock()

def init_db():
    """Creates the database tables.test change"""
	
    with app.app_context():
		print "creating database"
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
			db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        sqlite_db = sqlite3.connect(app.config['DATABASE'])
        sqlite_db.row_factory = sqlite3.Row
        top.sqlite_db = sqlite_db

    return top.sqlite_db


@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

@app.route(URL_PERFIX+'/requester',methods=['GET','POST'])
def requester():
    with  lock:
		if request.method =='GET':
		   return render_template('Requester.html')
		else:
		  global requester_count
		  global worker_count
		  global voter_count
		
		  db = get_db()		
		  cur = db.execute('select max(id) from tasks')
		  row = cur.fetchall()
		  if row[0][0]:
				requester_count=row[0][0]+1
				worker_count.append(0)
				voter_count.append(0)
				task_flag.append(0)
		  else:
				requester_count=1
		  print 'request_count='+str(requester_count)
		  input=[(requester_count,request.form['tutorialtitle'],request.form.get('tutorialtypewebsite'),
		  request.form.get('tutorialtypevideo'),request.form.get('tutorialtypeaudio'),
		  request.form.get('tutorialtypedirections'),request.form.get('levelofexperience'),
		  request.form.get('knownInformation'),request.form['sampletutorial'],
		  request.form['comments'],crowdlib_settings.cls.default_max_assignments ,crowdlib_settings.cls.default_max_assignments ,crowdlib_settings.cls.default_max_assignments ,request.form['skillstolearn'])]   
		  db.executemany('insert into tasks values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',input)
		  db.commit()
		  hit_type = cl.create_hit_type(
			  title = " Research project, Generous pay:Collect tutorials", 
			  description = "Research Project, Collect testing tutorials",
			  reward = 0.5
			  )
		  hit = hit_type.create_hit( url = "https://crowd.ecn.purdue.edu"+URL_PERFIX+"/collection/?taskId="+str(requester_count),  height = 800)	
    return redirect("https://crowd.ecn.purdue.edu"+URL_PERFIX+"/task_result/?taskId="+str(requester_count))
  
@app.route(URL_PERFIX+'/collection/',methods=['GET'])
def collectTutorials():
    with lock:	
		taskId='1'
		if 'taskId' in request.args:
			taskId=request.args['taskId']
		else:
			 return app.make_response('bad argument')
	
		assignmentId=''
		turkSubmitTo=''
		workerId=''
		hitId=''
		if 'assignmentId' in request.args:
			assignmentId=request.args['assignmentId']
		if 'workerId' in request.args:
			workerId=request.args['workerId']
		if 'turkSubmitTo' in request.args:
			turkSubmitTo=request.args['turkSubmitTo']
		if 	'hitId' in request.args:
			hitId=request.args['hitId']
		db = get_db()			
		cur = db.execute('select * from tasks where id=?',taskId)
		row = cur.fetchall()
	
		requesterTutorialTopic=row[0][1]
		requesterTutorialFormats=""
		tutorialwebsite=row[0][2]
		tutorialtypevideo=row[0][3]
		tutorialtypeaudio=row[0][4]
		tutorialtypedirections=row[0][5]
		if tutorialwebsite:
			requesterTutorialFormats=requesterTutorialFormats+tutorialwebsite+", "
		if tutorialtypevideo:
			requesterTutorialFormats=requesterTutorialFormats+tutorialtypevideo+", "
		if tutorialtypeaudio:
			requesterTutorialFormats=requesterTutorialFormats+tutorialtypeaudio+", "
		if tutorialtypedirections:
			requesterTutorialFormats=requesterTutorialFormats+tutorialtypedirections+", "
		requesterLevelOfDetail=row[0][6]
		alreadyknowninformation=row[0][7]
		sampletutuorial=row[0][8]
		requesterComments=row[0][9]
		desiredskill=row[0][13]
    return render_template('tutorialcollection.html',requesterTutorialTopic=requesterTutorialTopic,
	requesterTutorialFormats=requesterTutorialFormats,requesterLevelOfDetail=requesterLevelOfDetail,
	desiredskill=desiredskill,alreadyknowninformation=alreadyknowninformation,sampletutuorial=sampletutuorial,
	requesterComments=requesterComments,taskId=taskId,assignmentId=assignmentId,workerId=workerId,
	turkSubmitTo=turkSubmitTo,hitId=hitId,formsubmiturl=formsubmiturl)


@app.route(URL_PERFIX+'/tutorialcollection/',methods=['GET','POST'])
def addTutorial():
	with lock:
		title = request.form.get('title')
		resourcelink = request.form.get('resourcelink')
		mainContent = request.form.get('content')
		comment = request.form.get('comment')
		taskId = request.form.get('taskId')
		assignmentId=request.form.get('assignmentId')
		hitId=request.form.get('hitId')
		workerId=request.form.get('workerId')
		turkSubmitTo=request.form.get('turkSubmitTo')
	
		db = get_db()		
		cur = db.execute('select count(id) from tutorials where taskid=?',taskId)
		row = cur.fetchall()
		if row[0][0]:
			tutorial_count=row[0][0]+1
		else:
			tutorial_count = 1
		input=[(tutorial_count,taskId,title,resourcelink,mainContent,comment,assignmentId,hitId,workerId,turkSubmitTo,0,0)]   
		db.executemany('insert into tutorials values(?,?,?,?,?,?,?,?,?,?,?,?)',input)
		db.commit()
	
	
		hit_type = cl.create_hit_type(
			 title = "Research Project Generous pay: Evaluate testing tutorials", 
			 description = "Comment on tutorials.",
			 reward = 0.10)
		hit = hit_type.create_hit( url = "https://crowd.ecn.purdue.edu"+URL_PERFIX+"/evaluating/?taskId="+str(taskId)+"&tutorialId="+str(tutorial_count), height = 800)
	
		print "tutorial_count"+str(tutorial_count)
	return jsonify(result=1)
	

       
@app.route(URL_PERFIX+'/evaluating/',methods=['GET'])
def viewtutorial():
    with lock:
		taskId=''
		if 'taskId' in request.args:
			taskId=request.args['taskId']
		else:
			return app.make_response('bad argument')
	
		tutorialId='' 	
		if 'tutorialId' in request.args:
			tutorialId=request.args['tutorialId']
		else:
			return app.make_response('bad argument')

		assignmentId=''
		turkSubmitTo=''
		workerId=''
		hitId=''
		if 'assignmentId' in request.args:
			assignmentId=request.args['assignmentId']
		if 'workerId' in request.args:
			workerId=request.args['workerId']
		if 'turkSubmitTo' in request.args:
			turkSubmitTo=request.args['turkSubmitTo']
		if 	'hitId' in request.args:
			hitId=request.args['hitId']
	   
		db = get_db()
		cur1 = db.execute('select * from tasks where id=?',taskId)
		row1 = cur1.fetchall()
	
		requesterTutorialTopic=row1[0][1]
		requesterTutorialTopic = requesterTutorialTopic.replace("-","").replace("\r","").replace("\n","")
		requesterTutorialFormats=""
		tutorialwebsite=row1[0][2]
		tutorialtypevideo=row1[0][3]
		tutorialtypeaudio=row1[0][4]
		tutorialtypedirections=row1[0][5]
		if tutorialwebsite:
			requesterTutorialFormats=requesterTutorialFormats+tutorialwebsite+", "
		if tutorialtypevideo:
			requesterTutorialFormats=requesterTutorialFormats+tutorialtypevideo+", "
		if tutorialtypeaudio:
			requesterTutorialFormats=requesterTutorialFormats+tutorialtypeaudio+", "
		if tutorialtypedirections:
			requesterTutorialFormats=requesterTutorialFormats+tutorialtypedirections+", "
		requesterTutorialFormats = requesterTutorialFormats.replace("-","").replace("\r","").replace("\n","")
		requesterLevelOfDetail=row1[0][6]
		requesterLevelOfDetail = requesterLevelOfDetail.replace("-","").replace("\r","").replace("\n","")
		alreadyknowninformation=row1[0][7]
		alreadyknowninformation=alreadyknowninformation.replace("-","").replace("\r","").replace("\n","")
		sampletutuorial=row1[0][8]
		sampletutuorial =sampletutuorial.replace("-","").replace("\r","").replace("\n","")
		requesterComments=row1[0][9]
		requesterComments = requesterComments.replace("-","").replace("\r","").replace("\n","")
		desiredskill=row1[0][13]
		desiredskill = desiredskill.replace("-","").replace("\r","").replace("\n","")
	
		cur2 = db.execute('select * from tutorials where id=? and taskid=?',(tutorialId,taskId))
		row2 = cur2.fetchall()
	
		title = row2[0][2]
		title = title.replace("-","").replace("\r","").replace("\n","")
		resourcelink = row2[0][3]
		resourcelink = resourcelink.replace("-","").replace("\r","").replace("\n","")
		maincontent = row2[0][4]
		maincontent = maincontent.replace("-","").replace("\r","").replace("\n","")
		comment = row2[0][5]
		comment = comment.replace("-","").replace("\r","").replace("\n","")
    
    return render_template('Evaluatetutorials.html',requesterTutorialTopic=requesterTutorialTopic,
    requesterTutorialFormats=requesterTutorialFormats,requesterLevelOfDetail=requesterLevelOfDetail,
    desiredskill=desiredskill,alreadyknowninformation=alreadyknowninformation,sampletutuorial=sampletutuorial,
    requesterComments=requesterComments,assignmentId=assignmentId,workerId=workerId,turkSubmitTo=turkSubmitTo,
    hitId=hitId,taskId=taskId,tutorialId=tutorialId,workerTutorialTitle=title,workerTutorialContent=maincontent,
    workerTutorialResourceUrl=resourcelink,workerTutorialComment=comment,formsubmiturl=formsubmiturl)
   
          
@app.route(URL_PERFIX+'/tutorialevaluating/',methods=['GET','POST'])
def evaluatetutorial():
    with lock:
		taskId = request.form.get('taskId')
		tutorialId = request.form.get('tutorialId')
		count = 0
	 	 
		db = get_db()
		cur = db.execute('select * from tutorials where taskid=? and id= ? ',(taskId,tutorialId))
		row = cur.fetchall()
		yes_count = row[0][10]
		no_count = row[0][11]
	
		print(request.form.get('turkSubmitTo'))
		if request.form.get('vote')=='yes':
			yes_count=yes_count+1
			print("yes_count"+str(yes_count))
			db.execute('update tutorials set agree = ? where taskid= ? and id= ? ',(yes_count,taskId,tutorialId))
			db.commit()
		else:
			no_count=no_count+1
			print("no_count"+str(no_count))
			db.execute('update tutorials set disagree = ? where taskid= ? and id= ?',(no_count,taskId,tutorialId))
			db.commit()
		
		cur = db.execute('select sum(agree+disagree) from tutorials where taskid = ?',taskId)
		row = cur.fetchall()
		print ("total "+str(row[0][0]) +" votes")
		if row[0][0]>=(crowdlib_settings.cls.default_max_assignments *crowdlib_settings.cls.default_max_assignments ):
			print ("all tutorials has been verified on total "+str(row[0][0]) +" votes")
			cur1 = db.execute('select * from tutorials where taskid = ?',taskId)
			cur3 = db.execute('select count(id) from tutorials where taskid=?',taskId)
			row3 = cur3.fetchall()
			count = row3[0][0]
			for row1 in cur1.fetchall():
				if row1[10]<row1[11]:
					count = count-1
			if count:
			   hit_type = cl.create_hit_type(
					 title ="Research Project Generous pay: Vote on testing tutorials?", 
					 description = "Vote on tutorials",
					 reward = 0.10)
			   hit = hit_type.create_hit( url = "https://crowd.ecn.purdue.edu"+URL_PERFIX+"/voting/?taskId="+str(taskId), height = 800)
			else:
			   print "Goes back to tutorial collection"
			   hit_type = cl.create_hit_type(
					   title = "Research Project Generous pay: Collect testing tutorials",
					   description = "Collect testing tutorials",
					   reward =0.5
					   )
			   hit = hit_type.create_hit( url = "https://crowd.ecn.purdue.edu"+URL_PERFIX+"/collection/?taskId="+str(taskId),height = 800)

    return jsonify(result=1)

@app.route(URL_PERFIX+'/voting/',methods=['GET'])
def review():
    with lock:
		taskId=''
		if 'taskId' in request.args:
			taskId=request.args['taskId']
		else:
			return app.make_response('bad argument')
		
		assignmentId=''
		turkSubmitTo=''
		workerId=''
		hitId=''
		if 'assignmentId' in request.args:
			assignmentId=request.args['assignmentId']
		if 'workerId' in request.args:
			workerId=request.args['workerId']
		if 'turkSubmitTo' in request.args:
			turkSubmitTo=request.args['turkSubmitTo']
		if 	'hitId' in request.args:
			hitId=request.args['hitId']
		
		db = get_db()
		cur1 = db.execute('select * from tasks where id = ?',taskId)
		row1 = cur1.fetchall()
		print row1
		requesterTutorialTopic=row1[0][1]
		requesterTutorialTopic = requesterTutorialTopic.replace("-","").replace("\r","").replace("\n","")
		requesterTutorialFormats=""
		tutorialwebsite=row1[0][2]
		tutorialtypevideo=row1[0][3]
		tutorialtypeaudio=row1[0][4]
		tutorialtypedirections=row1[0][5]
		if tutorialwebsite:
		   requesterTutorialFormats=requesterTutorialFormats+tutorialwebsite+", "
		if tutorialtypevideo:
		   requesterTutorialFormats=requesterTutorialFormats+tutorialtypevideo+", "
		if tutorialtypeaudio:
		   requesterTutorialFormats=requesterTutorialFormats+tutorialtypeaudio+", "
		if tutorialtypedirections:
		   requesterTutorialFormats=requesterTutorialFormats+tutorialtypedirections+", "
		requesterTutorialFormats = requesterTutorialFormats.replace("-","").replace("\r","").replace("\n","")
		requesterLevelOfDetail=row1[0][6]
		requesterLevelOfDetail = requesterLevelOfDetail.replace("-","").replace("\r","").replace("\n","")
		alreadyknowninformation=row1[0][7]
		alreadyknowninformation = alreadyknowninformation.replace("-","").replace("\r","").replace("\n","")
		sampletutuorial=row1[0][8]
		sampletutuorial = sampletutuorial.replace("-","").replace("\r","").replace("\n","")
		requesterComments=row1[0][9]
		requesterComments = requesterComments.replace("-","").replace("\r","").replace("\n","")
		desiredskill=row1[0][13]
		desiredskill = desiredskill.replace("-","").replace("\r","").replace("\n","")
	
		cur2 = db.execute('select * from tutorials where agree >= disagree and taskid = ?  ', taskId)
		tutorials = [dict(id=row2[0], title=row2[2],content=row2[4],agree=row2[10],disagree=row2[11]) for row2 in cur2.fetchall()]
	    
    return render_template('Votetutorials.html',requesterTutorialTopic=requesterTutorialTopic,
    requesterTutorialFormats=requesterTutorialFormats,requesterLevelOfDetail=requesterLevelOfDetail,
    desiredskill=desiredskill,alreadyknowninformation=alreadyknowninformation,sampletutuorial=sampletutuorial,
    requesterComments=requesterComments,taskId=taskId,assignmentId=assignmentId,workerId=workerId,turkSubmitTo=turkSubmitTo,
    hitId=hitId,tutorials = tutorials,formsubmiturl=formsubmiturl)

@app.route(URL_PERFIX+'/tutorialvoting/',methods=['GET','POST'])
def voting():
	
	with lock:
		print ("tutorialvoting")
		taskId = request.form.get('taskId')
		tutorial1 = request.form.get('vote1')
		tutorial2 = request.form.get('vote2')
		assignmentId = request.form.get('assignmentId')
		hitId = request.form.get('hitId')
		workerId = request.form.get('workerId')
		turkSubmitTo = request.form.get('turkSubmitTo')
		votes_count = 0
		
		
		db = get_db()
		input=[(taskId,tutorial1,tutorial2,assignmentId,hitId,workerId,turkSubmitTo)]   
		db.executemany('insert into votes values(?,?,?,?,?,?,?)',input)
		db.commit()
		
			
		cur = db.execute('select count(*) from votes where taskid=?',taskId)
		row = cur.fetchall()
		if row[0][0]:
			votes_count=row[0][0]+1
		print 'voter_count'+str(votes_count)
		
		if votes_count >= crowdlib_settings.cls.default_max_assignments :
			print ("all done ")
			
	return jsonify(result=1)
       
    
@app.route(URL_PERFIX+'/result/',methods=['GET'])
def result():
   with lock:
	   db = get_db()
	   cur1 = db.execute('select * from tasks')
	   tasks = [dict(field1=row[0],field2=row[1],field3=row[2],field4=row[3],field5=row[4],
	   field6=row[5],field7=row[6],field8=row[7],field9=row[8],field10=row[9],filed11=row[10],
	   fiels12=row[11],filed13=row[12],field14=row[13]) for row in cur1.fetchall()]
   
	   cur2 = db.execute('select * from tutorials ')
	   tutorials = [dict(field1=row[0],field2=row[1],field3=row[2],field4=row[3],field5=row[4],
	   field6=row[5],field7=row[6],field8=row[7],field9=row[8],field10=row[9],field11=row[10],field12=row[11]) for row in cur2.fetchall()]
   
	   cur3 = db.execute('select * from votes') 
	   votes = [dict(field1=row[0],field2=row[1],field3=row[2],filed4=row[3],field5=row[4],field6=row[5],field7=row[6]) for row in cur3.fetchall()]
   
   return render_template('result.html', tasks=tasks,tutorials=tutorials,votes=votes)

@app.route(URL_PERFIX+'/task_result/',methods=['GET'])
def task_result():
	with lock:
	   taskId=''
	   if 'taskId' in request.args:
			taskId=request.args['taskId']
	   else:
			return app.make_response('bad argument')
   
	   db = get_db()
	   cur1 = db.execute('select count(*) from votes where taskid=?',taskId)
	   row1 = cur1.fetchall()
	   if row1[0][0]>= crowdlib_settings.cls.default_max_assignments:
		  db = get_db()
		  cur = db.execute('select * from votes where taskid = ?',taskId) 
		  votes = [dict(field1=row[0],field2=row[1],field3=row[2],filed4=row[3],field5=row[4],field6=row[5],field7=row[6]) for row in cur.fetchall()]
		  return render_template('task_result.html', votes=votes)     
	return render_template('noresult.html')

if __name__== '__main__':
	#init_db()
	app.run(host="127.0.0.1", port= PORT,threaded = True)
	 



			
