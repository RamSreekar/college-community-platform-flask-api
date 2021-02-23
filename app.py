from flask import Flask,render_template,request, jsonify, redirect, url_for
import pymongo
import copy
from flask_cors import CORS, cross_origin
from bson import ObjectId
from bson.json_util import dumps,loads
from werkzeug.security import generate_password_hash, check_password_hash
import dns
import os

app = Flask(__name__)

CORS(app)
cors = CORS(app, resources={
		r"/*" : {
			"origins" : "*"
		}
	})

db_url = os.environ.get('MONGODB_CLUSTER_URL')
mongo = pymongo.MongoClient(db_url)


@app.route('/register', methods=['GET','POST'])
def register():
	usersDB = mongo.mcpDB.reg_users
	if request.method == 'POST':
		name = request.json['name']
		email = request.json['email']
		pwd = request.json['pwd']
		usertype = request.json['userType']
		hash_pass = generate_password_hash(pwd)
		reg_user = usersDB.find_one({'email':email})
		if not reg_user:
			res = usersDB.insert_one({'name':name, 'email':email, 'pwd':hash_pass, 'userType':usertype})
			x = {
			    "name": name,
			    "email": email,
			    "pwd": pwd,
			    "userType" : usertype,
			    "status" : 200
			}
			if res:
				return jsonify(x)
			else:
				err1 =  {
					"Error" : 'Insert not successful', 
			    	"status" : 202
			    } 

		else:
			err = {
				"Error" : 'User already Registered', 
			    "status" : 202
			    }
			return jsonify(err)	

	if request.method == 'GET':
		return '<h1>College Community Platform - Register</h1>'

		
@app.route('/login',methods=['GET','POST'])
def login():
	usersDB = mongo.mcpDB.reg_users
	if request.method == 'POST':
		email = request.json['email']
		pwd = request.json['pwd']
		reg_user = usersDB.find({'email' : email})
		user = copy.deepcopy(reg_user)
			
		if list(reg_user):
			user2 = list(user)
			print(user2)
			dbpwd = str(user2[0]['pwd'])
			matched = check_password_hash(dbpwd, pwd)
			print('\n\nmatched : '+str(matched)+'\n\n')
			if matched:
				ut = user2[0]['userType']
				uname = user2[0]['name']

				valid_user = {
					"email" : email,
					"name" : uname,
					"userType" : ut,
					"status" : 200
				}
				return jsonify(valid_user)
			else:
				login_error = {
				"Error" : 'Incorrect password',
				"status" : 202
			}
			return jsonify(login_error)

		else:
			print(list(reg_user))
			invalid_user = {
				"Error" : 'User not registered',
				"status" : 202
			}
			return jsonify(invalid_user)

	if request.method == 'GET':
		return '<h1>College Community Platform - Login</h1>'


@app.route('/discussion-forum/ask',methods=['GET','POST'])
def ask():
	quesDB = mongo.mcpDB
	if request.method == 'POST':
		branch = request.json['branch']
		ques = request.json['question']
		timestamp = request.json['timestamp']
		author = request.json['author']
		data ={'question':ques, 'author':author, 'timestamp':timestamp, "branchId":branch}
		if branch == 732   : res = quesDB.CIVIL.insert_one(data)
		elif branch == 733 : res = quesDB.CSE.insert_one(data)
		elif branch == 734 : res = quesDB.EEE.insert_one(data)
		elif branch == 735 : res = quesDB.ECE.insert_one(data)
		elif branch == 736 : res = quesDB.MECH.insert_one(data)
		elif branch == 737 : res = quesDB.IT.insert_one(data)
		elif branch == 100 : res = quesDB.GENERAL.insert_one(data)
		else: 
			err = {
				"status":202
			}
			return jsonify(err)
		if res:
			ok = {
				"status":200
			}
			return jsonify(ok)
		else:
			err2 = {
				"status":202,
				"Error":'Insert unsuccessful'
			}
			return err2

	if request.method == 'GET':
		return '<h1>College Community Platform - Ask Question</h1>'

		
@app.route('/discussion-forum/view_all',methods=['GET','POST'])
def view_all():
	quesDB = mongo.mcpDB
	if request.method == 'POST':
		branch = request.json['branch']
		if branch == 732   : all_ques = quesDB.CIVIL.find()
		elif branch == 733 : all_ques = quesDB.CSE.find()
		elif branch == 734 : all_ques = quesDB.EEE.find()
		elif branch == 735 : all_ques = quesDB.ECE.find()
		elif branch == 736 : all_ques = quesDB.MECH.find()
		elif branch == 737 : all_ques = quesDB.IT.find()
		elif branch == 100 : all_ques = quesDB.GENERAL.find()
		else: 
			err = {
				"status":202,
				"Error" : "Invalid Branch Code"
			} 
			return jsonify(err)

		qdata = copy.deepcopy(all_ques)
		if not qdata:
			err2 = {
				"status":200,
				"Description" : "No questions posted yet !!!"
			}
			return jsonify(err2)
		else:
			output = {'result':{}}
			i = 0
			for x in all_ques:
				output['result'][str(i)] = x
				y = output['result'][str(i)].pop('_id') 
				output['result'][str(i)]['qid'] = str(y) 
				i += 1
			output.update(status=200)
			return jsonify(output)
	
	if request.method == 'GET':
		return '<h1>College Community Platform - viewall-discussion forum</h1>'	


@app.route('/discussion-forum/ques_data',methods=['GET','POST'])
def ques_data():
	quesDB = mongo.mcpDB
	if request.method == 'POST':
		branch = request.json['branch']
		qid = request.json['qid']
		data = {"_id" : ObjectId(qid)}
		if branch == 732   : ques_data = quesDB.CIVIL.find(data)
		elif branch == 733 : ques_data = quesDB.CSE.find(data)
		elif branch == 734 : ques_data = quesDB.EEE.find(data)
		elif branch == 735 : ques_data = quesDB.ECE.find(data)
		elif branch == 736 : ques_data = quesDB.MECH.find(data)
		elif branch == 737 : ques_data = quesDB.IT.find(data)
		elif branch == 100 : ques_data = quesDB.GENERAL.find(data)
		else :
			err = {
				"status":202,
				"Error" : "Invalid Branch Code."
			}
			return jsonify(err)

		qdata = copy.deepcopy(ques_data)
		if not list(qdata):
			msg = {
				"status":202,
				"Error" : "Invalid QuestionId in that branch."
			}
			return jsonify(msg)
		else:
			output = {'result':{}}
			i = 0
			for x in ques_data:
				output['result'][str(i)] = x
				y = output['result'][str(i)].pop('_id') 
				output['result'][str(i)]['qid'] = str(y) 
				i += 1
			output.update(status=200)
			return jsonify(output)

	if request.method == 'GET':
		return '<h1>College Community Platform - question data-discussion forum</h1>'

	
@app.route('/discussion-forum/post_reply',methods=['GET','POST'])
def post_reply():
	quesDB = mongo.mcpDB
	if request.method == 'POST':
		qid = request.json['qid']
		branch = request.json['branch']
		timestamp = request.json['timestamp']
		author = request.json['author']
		reply = request.json['reply']
		author_name = author[:author.index('@')]
		r = {"qid" : qid,
			"r_author" : author,
			"r_timestamp" : timestamp,
			"reply" :reply}
		rstring = str(branch)+'/'+author_name+'/'+timestamp 
		key_string = "replies."+rstring
		data = {"$set":{key_string:r}}
		
		if branch == 732   : quesDB.CIVIL.update_one({"_id" : ObjectId(qid)},data)
		elif branch == 733 : quesDB.CSE.update_one({"_id" : ObjectId(qid)},data)
		elif branch == 734 : quesDB.EEE.update_one({"_id" : ObjectId(qid)},data)
		elif branch == 735 : quesDB.ECE.update_one({"_id" : ObjectId(qid)},data)
		elif branch == 736 : quesDB.MECH.update_one({"_id" : ObjectId(qid)},data)
		elif branch == 737 : quesDB.IT.update_one({"_id" : ObjectId(qid)},data)
		elif branch == 100 : quesDB.GENERAL.update_one({"_id" : ObjectId(qid)},data)
		else: 
			err = {
				"status":202
			}
			return jsonify(err)

		ok = {
			"status":200
		}
		return jsonify(ok)

	if request.method == 'GET':
		return '<h1>College Community Platform - post reply-discussion forum</h1>'	


@app.route("/opportunities/post",methods=['GET','POST'])
def post_opp():
	oppDB = mongo.mcpDB.opportunities
	if request.method == 'POST':
		o_title = request.json['title']
		o_content = request.json['content']
		o_author = request.json['author']
		o_timestamp = request.json['timestamp']
		link = request.json['link']
		data = {"title":o_title, "content":o_content, "author":o_author, 
				"timestamp":o_timestamp, "link":link}
		res = oppDB.insert_one(data)
		ok = {"status":200}
		failure = {"status":202}
		if res:
			return jsonify(ok)
		else:
			return jsonify(failure)

	if request.method == 'GET':
		return '<h1>College Community Platform - post - opportunity</h1>'

@app.route("/opportunities/view",methods=['GET'])
def view_opp():
	oppDB = mongo.mcpDB.opportunities
	all_posts = oppDB.find()
	posts = copy.deepcopy(all_posts)
	if not posts:
		msg = {
			"status" : 200,
			"Description" : "No posts available yet."
		}
		return jsonify(msg)
	else:
		output = {'result':{}}
		i = 0
		for x in all_posts:
			output['result'][str(i)] = x
			y = output['result'][str(i)].pop('_id') 
			output['result'][str(i)]['postId'] = str(y) 
			i += 1
		output.update(status=200)
		return jsonify(output)


@app.route('/opportunities/opp_data',methods=['GET','POST'])
def opp_data():
	oppDB = mongo.mcpDB.opportunities
	if request.method == 'POST':
		oppid = request.json['oppId']
		opp_post = oppDB.find_one({"_id":ObjectId(oppid)})
		if opp_post:
			output = {'result':{}}
			output['result'] = opp_post
			pid = output['result'].pop('_id')
			output['result']['oppId'] = str(pid)
			output["status"] = 200
			return jsonify(output)
		else:
			err = {
				"status" : 202,
				"Description" : "Invalid post Id"
			}
			return jsonify(err)

	if request.method == 'GET':
		return '<h1>College Community Platform - opportunity data</h1>'

			
@app.route('/announcements/post',methods=['GET','POST'])
def post_ann():
	annDB = mongo.mcpDB.announcements
	if request.method == 'POST':
		a_title = request.json['title']
		a_content = request.json['content']
		a_author = request.json['author']
		a_timestamp = request.json['timestamp']
		a_imageUrl = request.json['imageUrl']
		link = request.json['link']
		data = {"title":a_title, "content":a_content, "author":a_author, 
				"timestamp":a_timestamp, "link":link, "imageUrl":a_imageUrl}
		res = annDB.insert_one(data)
		ok = {"status":200}
		failure = {"status":202}
		if res:
			return jsonify(ok)
		else:
			return jsonify(failure)

	if request.method == 'GET':
		return '<h1>College Community Platform - post - announcments</h1>'


@app.route("/announcements/view",methods=['GET'])
def view_ann():
	oppDB = mongo.mcpDB.announcements
	all_posts = oppDB.find()
	posts = copy.deepcopy(all_posts)
	if not posts:
		msg = {
			"status" : 200,
			"Description" : "No announcements yet."
		}
		return jsonify(msg)
	else:
		output = {'result':{}}
		i = 0
		for x in all_posts:
			output['result'][str(i)] = x
			y = output['result'][str(i)].pop('_id') 
			output['result'][str(i)]['postId'] = str(y) 
			i += 1
		output.update(status=200)
		return jsonify(output)


@app.route("/admin/view_users",methods=['GET'])
def view_users():
	db = mongo.mcpDB.reg_users
	all_users = db.find()
	output = {'users':{}}
	i = 0
	for x in all_users:
		output['users'][str(i)] = x
		y = output['users'][str(i)].pop('_id') 
		output['users'][str(i)]['userId'] = str(y) 
		i += 1
	output["status"] = 200
	return jsonify(output)


@app.route("/admin/user_data",methods=['GET','POST'])
def user_data():
	db = mongo.mcpDB.reg_users
	if request.method == 'POST':
		uid = request.json['userId']
		udata = db.find_one({"_id":ObjectId(uid)})

		if not list(udata):
			msg = {
				"status":202,
				"Error" : "Invalid userId."
			}
			return jsonify(msg)
		else:
			output = {'result':{}}
			output['result'] = udata
			uid = output['result'].pop('_id')
			output['result']['userId'] = str(uid)
			output["status"] = 200
			return jsonify(output) 

	if request.method == 'GET':
		return '<h1>College Community Platform - admin - user data</h1>'


@app.route('/admin/delete_user',methods=['GET','POST'])
def delete_user():
	db = mongo.mcpDB.reg_users
	if request.method == 'POST':
		uid = request.json['userId']
		res = db.delete_one({"_id":ObjectId(uid)})
		ok = {"status":200}
		failure = {"status":202, "Error":"Invalid userId"}
		if res:
			return jsonify(ok)
		else:
			return jsonify(failure)

	if request.method == 'GET':
		return '<h1>College Community Platform - admin - delete user</h1>'


@app.route('/admin/delete_opp',methods=['GET','POST'])
def delete_opp():
	db = mongo.mcpDB.opportunities
	if request.method == 'POST':
		oppid = request.json['oppId']
		res = res = db.delete_one({"_id":ObjectId(uid)})
		ok = {"status":200}
		failure = {"status":202, "Error":"Invalid oppId"}
		if res:
			return jsonify(ok)
		else:
			return jsonify(failure)

	if request.method == 'GET':
		return '<h1>College Community Platform - admin - delete opportunity post</h1>'


@app.route("/admin/all_users",methods=['GET'])
def all_users():
	db = mongo.mcpDB.reg_users
	all_users = db.find()
	output = {'users':[]}
	i = 0
	for x in all_users:
		output['users'].append(x)
		y = output['users'][i].pop('_id') 
		output['users'][i]['userId'] = str(y) 
		i += 1
	output["status"] = 200
	return jsonify(output)


if __name__ == "__main__":
	app.run()

