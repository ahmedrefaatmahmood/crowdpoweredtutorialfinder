#!/usr/local/bin/python2.9
import flask, random, os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request,session,g,redirect,url_for,abort,render_template,flash,json,jsonify
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

     
PORT=8001
URL_PERFIX='/%02d'%(PORT%100)

# configuration
DATABASE = 'sqlite_db'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
formsubmiturl="https://workersandbox.mturk.com/mturk/externalSubmit"

requester_count=0
worker_count=0
yes_count=0
no_count=0
tutorials=['t1','t2','t3','t4','t5','t6','t7','t8','t9','t10']

def init_db():
    """Creates the database tables."""
	
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
    if request.method =='GET':
       return render_template('Requester_1.html')
    else:
		global requester_count
		
		db = get_db()		
		cur = db.execute('select max(id) from tasks')
		row = cur.fetchall()
		if row[0][0]:
			requester_count=row[0][0]+1
		else:
			requester_count=1
		print requester_count
		input=[(requester_count,request.form['tutorialtitle'],request.form.get('tutorialwebsite'),
		request.form.get('tutorialtypevideo'),request.form.get('tutorialtypeaudio'),
		request.form.get('tutorialtypedirections'),request.form.get('levelofexperience'),
		request.form.get('knownInformation'),request.form['sampletutorial'],
		request.form['budget'],request.form['blacklist'],request.form['comments'],crowdlib_settings.cls.default_max_assignments ,crowdlib_settings.cls.default_max_assignments ,crowdlib_settings.cls.default_max_assignments ,request.form['skillstolearn'])]   
		print input
		db.executemany('insert into tasks values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',input)
		db.commit()
		hit_type = cl.create_hit_type("Label the following?", "Annotate simple text.")

		hit = hit_type.create_hit( url = "https://crowd.ecn.purdue.edu/01/collection/?taskId="+str(requester_count),  height = 800)
		print hit_type.preview_url	

		return render_template('Requester_1.html')

@app.route(URL_PERFIX+'/collection/',methods=['GET','POST'])
def collectTutorials():
	
	taskId=''
	if 'taskId' in request.args:
		taskId=request.args['taskId']
	else:
		return make_response('bad argument', 400)
		
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
	print taskId		
	cur = db.execute('select * from tasks where id=?',taskId)
	row = cur.fetchall()
	print row
	
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
	alreadyknowinformation=row[0][7]
	sampletutuorial=row[0][8]
	requesterComments=requesterComments=row[0][11]
	desiredskill=requesterComments=row[0][15]
	return render_template('tutorialcollection.html',requesterTutorialTopic=requesterTutorialTopic,
    requesterTutorialFormats=requesterTutorialFormats,requesterLevelOfDetail=requesterLevelOfDetail,desiredskill=desiredskill,alreadyknowinformation=alreadyknowinformation,
    sampletutuorial=sampletutuorial,requesterComments=requesterComments,taskId=taskId,assignmentId=assignmentId,workerId=workerId,turkSubmitTo=turkSubmitTo,hitId=hitId,formsubmiturl=formsubmiturl)


@app.route(URL_PERFIX+'/addtutorial/',methods=['GET','POST'])
def addTutorial():
	
	print request.args
	title = request.args.get('title')
	resourcelink = request.args.get('resourcelink')
	mainContent = request.args.get('content')
	comment = request.args.get('comment')
	taskId = request.args.get('taskId')
	assignmentId=request.args.get('assignmentId')
	hitId=request.args.get('hitId')
	workerId=request.args.get('workerId')
	turkSubmitTo=request.args.get('turkSubmitTo')
	print title
	print resourcelink
	print mainContent
	print comment
	print taskId
	print assignmentId
	print hitId
	print workerId
	print turkSubmitTo
	hit_type = cl.create_hit_type("Label the following?", "Annotate simple text.")

	hit = hit_type.create_hit( url = "https://crowd.ecn.purdue.edu/01/collection/?taskId="+str(requester_count),  height = 800)
#		requester_count=requester_count+1
	print hit_type.preview_url
	
	tutorial_count=1	
	db = get_db()		
	cur = db.execute('select count(id) from tutorials where taskid=?',taskId)
	row = cur.fetchall()
	if row[0][0]:
		tutorial_count=row[0][0]+1
	input=[(tutorial_count,taskId,title,resourcelink,mainContent,comment,assignmentId,hitId,workerId,turkSubmitTo)]   
	db.executemany('insert into tutorials values(?,?,?,?,?,?,?,?,?,?)',input)
	db.commit()
	print tutorial_count
	print "tutorial_count"+str(tutorial_count)
	tutorial_replications=0	
	db = get_db()		
	cur = db.execute('select tutorialcollectionreplciations from tasks where id=?',taskId)
	row = cur.fetchall()
	if row[0][0]:
		tutorial_replications=row[0][0]
	print "tutorial_replications"+str(tutorial_replications)
	db.commit()
	if tutorial_count>=tutorial_replications :
		hit_type = cl.create_hit_type("Comment on the following tutorial?", "Comment on the following tutorial.")
		hit = hit_type.create_hit( url = "https://crowd.ecn.purdue.edu/01/evaluating/?taskId="+str(taskId)+"&tutorialId="+str(tutorial_count),  height = 800)
		print hit_type.preview_url	
	
	return jsonify(result=1)







		

       
@app.route(URL_PERFIX+'/evaluating/',methods=['GET','POST'])
def worker2():
    if request.method =='GET':
       cur1 = g.db.execute('select * from requester')
       row1 = cur1.fetchall()
       print row1
       cur2 = g.db.execute('select * from worker1')
       row2 = cur2.fetchone()
       return render_template('worker2_1.html')
    else:
          if request.form.get('vote')=='yes':
             global yes_count
             yes_count=yes_count+1
             g.db.execute('update worker1 set agree = ? where workid= ?',(yes_count,0))
             g.db.commit()
          else:
             global no_count
             no_count=no_count+1
             g.db.execute('update worker1 set disagree = ? where workid= ?',(no_count,0))
             g.db.commit()
          print yes_count
          print no_count
          return redirect(url_for('result'))

@app.route(URL_PERFIX+'/voting/',methods=['GET','POST'])
def worker3():
    if request.method =='GET':
       cur = g.db.execute('select *from worker1')
       row = cur.fetchall()
       return render_template('worker3_1.html',field1=row[0][0])
    else:
       
       return redirect(url_for('result'))
       
    
@app.route('/result')
def result():
   cur1 = g.db.execute('select * from requester')
   requester = [dict(field1=row[0],field2=row[1],field3=row[2],field4=row[3],field5=row[4],
   field6=row[5],field7=row[6],field8=row[7],field9=row[8],field10=row[9],filed11=row[10]) for row in cur1.fetchall()]
   print requester
   cur2 = g.db.execute('select * from worker1')
   worker1 = [dict(field1=row[0],field2=row[1],field3=row[2],field4=row[3],field5=row[4],
   field6=row[5],field7=row[6],field8=row[7],field9=row[8],field10=row[9],field11=row[10]) for row in cur2.fetchall()]
   cur3 = g.db.execute('select * from worker3')
   worker3 = [dict(field1=row[0],field2=row[1],field3=row[2],field4=row[3],field5=row[4],
   field6=row[5],field7=row[6],field8=row[7],field9=row[8],field10=row[9],field11=row[10]) for row in cur3.fetchall()]
   return render_template('result.html', requester=requester,worker1=worker1,worker3=worker3)
   
            

if __name__== '__main__':
#	init_db()
	app.run(host="127.0.0.1", port=8001)
	 



