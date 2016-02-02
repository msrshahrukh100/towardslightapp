from towardslightapp import app
from flask import render_template,json,request,redirect,session,url_for ,jsonify,flash,send_from_directory
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from werkzeug import secure_filename
from werkzeug.wsgi import LimitedStream
import uuid
import os
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail , Message
from datetime import datetime
import MySQLdb
import random,string
from flask import session as login_session
from forms import LoginForm
from flask.ext.socketio import emit, join_room, leave_room


from flask.ext.socketio import SocketIO

socketio = SocketIO()



mail=Mail(app)
mysql = MySQL()


ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

'''
UPLOAD_FOLDER="/home/oldbooks/mysite/static/uploads/"
UPLOADT_FOLDER="/home/oldbooks/mysite/static/uploadst/" 
ALLOWED_EXTENSIONS=set(['png','jpg','jpeg','gif','tif','pdf'])
'''
@app.route('/',methods=['GET'])
def home():
    return render_template("homepage.html")


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32) )
    login_session['state'] = state
    return render_template('login.html')


#########################################for thechat####################################

@app.route('/letschat', methods=['GET', 'POST'])
def index():
    """"Login form to enter a room."""
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['room'] = form.room.data
        return redirect(url_for('chat'))
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
    return render_template('index.html', form=form)


@app.route('/chat')
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('index'))
    return render_template('chat.html', name=name, room=room)

@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def left(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    emit('message', {'msg': session.get('name') + ':' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)


#########################################################################################


@app.route('/confirm/<token>',methods=['GET','POST'])
def confirm_email(token):
    try:
        email = ts.loads(token,salt = "email-confirm-key" , max_age = None)
    except:
        abort(404)
    con = mysql.connect()
    cursor = con.cursor()
    cursor.callproc('confirmemail',(email,))
    con.commit()
    cursor.close() 
    con.close()
    return render_template("confirmed.html")

@app.route('/recover/<token>',methods=['GET','POST'])
def recover_email(token):
    try:
        email = ts.loads(token,salt = "password-recovery" , max_age = None)
    except:
        abort(404)

    try:
        newpw = request.form['inputPassword']
        _hashed_password = generate_password_hash(newpw)
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('changepw',(email,_hashed_password))
        con.commit()
        cursor.close() 
        con.close()
        flash ("Password reset successful!! Login with your new credentials")
        return render_template("homepage.html")
    except:
        return render_template("resetpw.html",token=token)
    
        



@app.route('/forgotpw',methods=['GET','POST'])
def fpw():
    if request.method=='POST':
        try:
            _email = request.form['inputEmail']
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('cavail',(_email,))
            data = cursor.fetchall()
            x=int(data[0][0])
            if x == 0:
                return jsonify(msg="Sorry this email is not registered with us")
            else :

                con = mysql.connect()
                cursor = con.cursor()
                cursor.callproc('checkconfirm',(_email,))
                data = cursor.fetchall()
                y=int(data[0][0])
                if y == 0:
                    return jsonify(msg="Sorry this email is not confirmed yet.If you wish to receive the confirmation code again click <a href='/getconfirm'>here</a>")
                else:
                    token = ts.dumps(_email, salt='password-recovery')
                    message = url_for('recover_email',token=token,_external=True)
                    html=render_template("pwrecoverymail.html",message=message)
                    return jsonify(msg=smail(_email,html))
        except Exception as e:
            return render_template('error.html',error = str(e))
        finally:
            cursor.close() 
            con.close()
    return render_template("forgotpw.html")






def smail(email,content):
    try:
        msg = Message("Towards Light",
        sender="msr.concordfly@gmail.com",
        recipients=[email])
        #msg.body=content
        msg.html=content
        mail.send(msg)
        return 'A mail has been sent to your email id.Please do check it!'
    except Exception as e:
        return str(e)






@app.route('/fsignup',methods=['POST','GET'])
def frontsignup():
 
    _name = request.form['sname']
    _email = request.form['semail']
    _password = request.form['spassword']
    _cpassword = request.form['scpassword']
    _tos = request.form['tos']
    con = mysql.connect()
    cursor = con.cursor()
    cursor.callproc('cavail',(_email,))
    data = cursor.fetchall()
    x=int(data[0][0])
    s1='@'
    s2='.'
    c1=0
    c2=0
    if(s1 in _email):
        c1=1
    if(s2 in _email):
        c2=1
    if(_email == "" or c1==0 or c2==0 ):
        return jsonify(ierror='Please enter a valid email id')          
    if x==0 :
        if _password == _cpassword and _password != "" :
            if(_tos == "Agree"):
                _hashed_password = generate_password_hash(_password)
                con = mysql.connect()
                cursor = con.cursor()
                cursor.callproc('frontpagesignup',(_name,_email,_hashed_password))
                con.commit()
                token = ts.dumps(_email, salt='email-confirm-key')
                message = url_for('confirm_email',token=token,_external=True)
                html=render_template("confirmationmail.html",message=message)
                return jsonify(success=smail(_email,html)) 
            else:
                return jsonify(success="You need to accept the terms of service!")
        else :              
            return jsonify(perror='Passwords dont match!')
    else :
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('checkconfirm',(_email,))
        data = cursor.fetchall()
        y = int(data[0][0])
        if y == 0:
            return jsonify(ierror='This id has been taken up but has not yet been confirmed.<br><a href="/getconfirm">Receive Confirmation Code</a>')
        else:
            return jsonify(ierror='Sorry this mail id has already been taken!')


   








@app.route('/test',methods=['GET','POST'])
def test():
    return render_template('test2.html')



@app.route('/upload2', methods=['GET', 'POST'])
def upload2():
    if request.method == 'POST':
        
        userid = session['user']
        file = request.files['file']
        extension = os.path.splitext(file.filename)[1]
        f_name = str(uuid.uuid4()) + extension
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('updateppic',(userid,f_name))
        data = cursor.fetchall()
        con.commit()
        cursor.close()
        con.close()
        return json.dumps({'filename':f_name})

        
    


@app.route('/viewaddpost')
def viewaddpost():
	return render_template('addpost.html')



@app.route('/viewupdateprofile')
def viewupdateprofile():
	return render_template('signup.html')


@app.route('/userhome')
def userhome():
    if session.get('user'):
        return render_template('userhome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

##########################earlier sign up
@app.route('/updateprofile',methods=['POST','GET'])
def updateprofile():
    try:
        if session.get('user'):
            userid = session['user']
            fname = request.form['first_name']
            lname = request.form['last_name']
            date = request.form['date']
            atype = request.form.get('type')
            institute = request.form['institute']
            aoi = request.form['aoi']
            hobby = request.form['hobby']
            skills = request.form['skills']
            privacy = request.form['privacy']
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('updateinfo',(userid,fname,lname,date,atype,institute,aoi,hobby,skills,privacy))
            data = cursor.fetchall()
            con.commit()   
            return jsonify(msg="Profile Updated Successfully!")

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        con.close()


########for getting all info####


@app.route('/getallinfo',methods=['GET'])
def getallinfo():
    try:
        if session.get('user'):
            userid = session['user']
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('getallinfo',(userid,))
            data = cursor.fetchall()
            return jsonify(id=data[0][0],fname=data[0][1],lname=data[0][2],email=data[0][3],
            ppic=data[0][5],atype=data[0][6],institute=data[0][7],dob=data[0][8],areaoint=data[0][9],
            hobby=data[0][10],skills=data[0][11])
    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        con.close()



@app.route('/viewpersoninfo/<pid>',methods=['GET'])
def viewpersoninfo(pid):
    try:
        if session.get('user'):
            userid = pid
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('getallinfo',(userid,))
            data = cursor.fetchall()
            return jsonify(id=data[0][0],fname=data[0][1],lname=data[0][2],email=data[0][3],
            ppic=data[0][5],atype=data[0][6],institute=data[0][7],dob=data[0][8],areaoint=data[0][9],
            hobby=data[0][10],skills=data[0][11],privacy=data[0][13])
    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        con.close()




@app.route('/getallposts',methods=['GET'])
def getallposts():
    try:
        if session.get('user'):
            userid = session['user'][0][0]
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('getuserposts',(userid,))
            data = cursor.fetchall()

            send=[]
            for info in data :
                senddict = {
                'mid':info[0],
                'mtitle':info[1],
                'mbody':info[2],
                'posttype':info[3],
                'type':info[4],
                'date':str(info[5]),
                'userid':info[8] 
                }
                send.append(senddict)



            return json.dumps(send)
    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        con.close()




@app.route('/viewuserposts/<pid>',methods=['GET'])
def viewuserposts(pid):
    try:
        if session.get('user'):
            userid = pid
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('getuserposts',(userid,))
            data = cursor.fetchall()

            send=[]
            for info in data :
                senddict = {
                'mid':info[0],
                'mtitle':info[1],
                'mbody':info[2],
                'posttype':info[3],
                'type':info[4],
                'date':str(info[5]),
                'userid':info[8] 
                }
                send.append(senddict)



            return json.dumps(send)
    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        con.close()

#####"""


#################
@app.route('/addpost',methods=['POST','GET'])
def addpost():
    try:
        if session.get('user'):
            userid = session['user'] 
            _title = request.form['title']
            _post = request.form['posts']
            _type = request.form['type']
            postcat = request.form['typeofpost']
            
            if _title and _post and _type:

                con = mysql.connect()
                cursor = con.cursor()
                cursor.callproc('getallinfo',(userid,))
                data2 = cursor.fetchall()
                


                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.callproc('addpost',(userid,data2[0][1],data2[0][2],_title,_post,postcat,_type))
                data = cursor.fetchall()
                cursor.close()
                con.close()
                if len(data) is 0:
                    conn.commit()
                    return jsonify(message='Post Added successfully!')
                else:
                    return jsonify(message=str(data[0]))
            else:
                return jsonify(message='Please fill all the entries')
    
    except Exception as e:
        return json.dumps({'error':str(e)})
   


#
@app.route('/validateLogin',methods=['POST','GET'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
        
        
        # connect to mysql

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('validateLogin',(_username,))
        data = cursor.fetchall() 
        if len(data) > 0:
            if check_password_hash(str(data[0][4]),_password):
                con = mysql.connect()
                cursor = con.cursor()
                cursor.callproc('checkconfirm',(_username,))
                data = cursor.fetchall()
                cursor.close()
                con.close()
                y = int(data[0][0])
                if y == 0:
                    return jsonify(msg='You need to confirm your email before login.<br>If you wish to receive the confirmation link again click <a href="/getconfirm">here</a>')
                else:
                    con = mysql.connect()
                    cursor = con.cursor()
                    cursor.callproc('getlogincred',(_username,))
                    data2 = cursor.fetchall()
                    session['user'] = data2
                    cursor.close()
                    con.close()

                    return redirect('userhome')
            else:
                return jsonify(msg='Oops! Try again, invalid credentials')
        else:
            return jsonify(msg='Oops! Try again, invalid credentials')
            

    except Exception as e:
        return render_template('error.html',error = str(e))

   


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


# Route that will process the file upload
@app.route('/upload', methods=['POST','GET'])
def upload():
    if session.get('user') :
        userid = session['user']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('findpic',(userid,))
        data = cursor.fetchall()
        cursor.close()
        con.close()
        if(data[0][0] != 'default.jpg'):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], data[0][0]))
        earlier = data[0][0]

        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('updateppic',(userid,filename))
            data = cursor.fetchall()
            con.commit()
            cursor.close()
            con.close()

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('updateevery',(userid,earlier,filename))
            data = cursor.fetchall()
            con.commit()
            cursor.close()
            con.close()
        

            return jsonify(imagepath=filename)

@app.route('/showpost/<mid>')
def showpost(mid):
    return render_template("viewthepost.html",mid=mid)



@app.route('/suviewpost/<mid>',methods=['GET','POST'])
def suviewpost(mid):
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('getdpost',(mid,))
        data1 = cursor.fetchall()
        con.close
        cursor.close()
        dpost=[]
        for post in data1:
            postdict = {
            'title':post[1],
            'body':post[2],
            'postcat':post[3],
            'authorf':post[6],
            'authorl':post[7]
            }
            dpost.append(postdict)
        return json.dumps(dpost)
        
    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        con.close()





@app.route('/like/<mid>', methods=['POST','GET'])
def like(mid):
    if session.get('user') :
        userid = session['user'][0][0]
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('getallinfo',(userid,))
        data2 = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()




        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('likedpost',(data2[0][1],data2[0][2],data2[0][5],mid,userid))
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()

        return jsonify(msg=data,fname=data2[0][1],lname=data2[0][2],ppic=data2[0][5])


@app.route('/getdlike/<mid>', methods=['POST','GET'])
def getdlike(mid):
    if session.get('user') :
        userid = session['user']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('getdlikes',(mid,))
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()
        likes=[]
        for like in data:
            likesdict={
            'userf':like[1],
            'userl':like[2],
            'ppic':like[3]
            }
            likes.append(likesdict)

        return json.dumps(likes)


@app.route('/addcomment/<mid>', methods=['POST','GET'])
def addcomment(mid):
    if session.get('user') :
        userid = session['user']
        comment = request.form['comment']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('getallinfo',(userid,))
        data2 = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()

        
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('addcomment',(data2[0][1],data2[0][5],comment,mid,userid))
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()


        return jsonify(msg=comment,name=data2[0][1],pic=data2[0][5])


@app.route('/getdcomments/<mid>', methods=['POST','GET'])
def getdcomments(mid):
    if session.get('user') :
        userid = session['user']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('getdcomments',(mid,))
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()
        likes=[]
        for like in data:
            likesdict={
            'userf':like[1],
            'ppic':like[2],
            'comment':like[3]
            }
            likes.append(likesdict)

        return json.dumps(likes)


@app.route('/findpageno',methods=['GET'])
def findpageno():
    con = mysql.connect()
    cursor = con.cursor()
    cursor.execute('select count(*) from posts')
    data = cursor.fetchall()
    cursor.close() 
    con.close()
    if(data[0][0] % 4):
        pages = (data[0][0] // 4)+1
    else:
        pages = data[0][0] // 4
    return jsonify(msg=pages)







@app.route('/pagination/<int:pno>',methods=['GET','POST'])
def pagination(pno):

    pno = pno-1
    pno = pno * 4
    con = mysql.connect()
    cursor = con.cursor()
    cursor.callproc('getpageposts',(pno,))
    data = cursor.fetchall()
    cursor.close() 
    con.close()
    send=[]
    for info in data :
        senddict = {
        'mid':info[0],
        'mtitle':info[1],
        'mbody':info[2],
        'posttype':info[3],
        'type':info[4],
        'date':str(info[5]),
        'userf':info[6],
        'userl':info[7],
        'userid':info[8] 
        }
        send.append(senddict)
    return json.dumps(send)






@app.route('/meetpeoples')
def meetpeoples():
    
    return render_template('meetpeoples.html')


@app.route('/getallpeople', methods=['GET'])
def getallpeople():
    if session.get('user') :
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('getallpeople',())
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()
        peoples=[]
        for people in data:
            peoplesdict={
            'userid':people[0],
            'userf':people[1],
            'userl':people[2],
            'ppic':people[5],
            'type':people[6],
            'institution':people[7]
            }
            peoples.append(peoplesdict)

        return json.dumps(peoples)
    else:
        return "You need to be logged in!!"





@app.route('/viewperson/<pid>')
def viewperson(pid):
    
    return render_template('viewperson.html',pid=pid)




@app.route('/tazkira',methods=['GET','POST'])
def maketazkira():
    if session.get('user'):
        if request.method == 'POST' :
            userid = session['user']
            mestazkira = request.form['tazkira']
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('getallinfo',(userid,))
            data2 = cursor.fetchall()
            cursor.close()
            con.commit()
            con.close()
            time = str(datetime.now().strftime('%H:%M'))

            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('addtazkira',(mestazkira,data2[0][1],data2[0][2],time,userid))
            data = cursor.fetchall()
            cursor.close()
            con.commit()
            con.close()

            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('addconnection',(userid,userid))
            data = cursor.fetchall()
            cursor.close()
            con.commit()
            con.close()
            
            return jsonify(msg=mestazkira,time=time,userf=data2[0][1],userl=data2[0][2])
        else:
            userid = session['user'][0][0]
            #return jsonify(msg=userid)
            con = mysql.connect()
            cursor = con.cursor()
            cursor.execute('select * from tazkira where tdate = curdate() and userid in (select sender from connections where receiver = %d)'%userid)
            #cursor.callproc('gettazkira',(userid,))
            data = cursor.fetchall()
            cursor.close()
            con.commit()
            con.close()
            sendtaz=[]
            for taz in data:
                tazdict={
                'userf':taz[1],
                'userl':taz[2],
                'msg':taz[3],
                'time':taz[5]
                }
                sendtaz.append(tazdict)

            return json.dumps(sendtaz)





@app.route('/addfriend/<sender>', methods=['GET'])
def addfriend(sender):
    if session.get('user') :
        receiver = session['user']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('addconnection',(sender,receiver))
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()
        
        return jsonify(msg=data[0][0])
    else:
        return "You need to be logged in!!"




@app.route('/deleteconnection/<sender>', methods=['GET'])
def deleteconnection(sender):
    if session.get('user') :
        receiver = session['user']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('deleteconnection',(sender,receiver))
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()
        
        return jsonify(msg=data)
    else:
        return "You need to be logged in!!"




@app.route('/editdpost/<postid>', methods=['GET'])
def editpost(postid):
    if session.get('user') :
        return render_template('editthepost.html',postid=postid)
    else:
        return "You need to be logged in!!"

    
    

@app.route('/vieweditpage/<postid>', methods=['GET','POST'])
def vieweditpage(postid):
    if request.method == 'GET':
        if session.get('user') :
            userid = session['user']
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('checkeditpermission',(userid,postid))
            data = cursor.fetchall()
            cursor.close()
            con.commit()
            con.close()
            if(data[0][0]):
                con = mysql.connect()
                cursor = con.cursor()
                cursor.callproc('getdpost',(postid,))
                data2 = cursor.fetchall()
                cursor.close()
                con.commit()
                con.close()
                return jsonify(msg="Success",
                    ptitle=data2[0][1],
                    post=data2[0][2])
            else:
                return jsonify(msg="")
        else:
            return "You need to be logged in!!"
    else:
        if session.get('user'):
            userid = session['user']
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('checkeditpermission',(userid,postid))
            data3 = cursor.fetchall()
            cursor.close()
            con.commit()
            con.close()
            if(data3[0][0]):
                title = request.form['utitle']
                post = request.form['uposts']
                typeofpost = request.form['typeofpost']
                wtype = request.form['type']

                if title and post and typeofpost and wtype:
                    con = mysql.connect()
                    cursor = con.cursor()
                    cursor.callproc('updatepost',(postid,title,post,typeofpost,wtype))
                    data2 = cursor.fetchall()
                    cursor.close()
                    con.commit()
                    con.close()
                    return jsonify(msg="Post has been edited!")
                else:
                    return jsonify(msg="Please fill all the entries!")

    
    



@app.route('/editdpost/deletedpost/<postid>', methods=['GET'])
def deletedpost(postid):
    if session.get('user') :
        userid = session['user']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('deletedpost',(userid,postid))
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('deletedlikes',(postid,))
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('deletedcomments',(postid,))
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()
        
        return jsonify(msg="Deleted!!")
    else:
        return "You need to be logged in!!"


@app.route('/meetconnections')
def meetconnections():
    
    return render_template('meetconnections.html')



@app.route('/getallfriends', methods=['GET'])
def getallfriends():
    if session.get('user') :
        userid = session['user']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('getallfriends',(userid,))
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()
        peoples=[]
        for people in data:
            peoplesdict={
            'userid':people[0],
            'userf':people[1],
            'userl':people[2],
            'ppic':people[5],
            'type':people[6],
            'institution':people[7]
            }
            peoples.append(peoplesdict)

        return json.dumps(peoples)
    else:
        return "You need to be logged in!!"





@app.route('/dropmessage/<pid>', methods=['GET','POST'])
def dropmessage(pid):
    if session.get('user') :
        userid = session['user']
        message = request.form['dropmessage']
        if message :
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('getallinfo',(userid,))
            data2 = cursor.fetchall()
            cursor.close()
            con.commit()
            con.close()
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('dropmessage',(message,data2[0][1],data2[0][2],userid,pid,data2[0][5]))
            data = cursor.fetchall()
            cursor.close()
            con.commit()
            con.close()
            return jsonify(msg="Message Sent!")
        else:
            return jsonify(msg="Add a message to send!")
    else:
        return "You need to be logged in!!"




@app.route('/checkfriendship/<pid>', methods=['GET','POST'])
def checkfriendship(pid):
    if session.get('user') :
        userid = session['user']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('checkfriendship',(userid,pid))
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()
        return jsonify(status=data[0][0])
            
        
    else:
        return "You need to be logged in!!"




@app.route('/getmymessages', methods=['GET'])
def getmymessages():
    if session.get('user') :
        userid = session['user']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('getmymessages',(userid,))
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()
        mymessages=[]
        for message in data:
            msg_dict={
            'message':message[1],
            'userf':message[2],
            'userl':message[3],
            'ppic':message[6]
            }
            mymessages.append(msg_dict)
        return json.dumps(mymessages)
    else:
        return "You need to be logged in!!"




@app.route('/messagecenter')
def messagecenter():
    
    return render_template('messagecenter.html')



@app.route('/seenmessages', methods=['GET'])
def seenmessages():
    if session.get('user') :
        userid = session['user']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('seemessages',(userid,))
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()
        return jsonify(msg="Seen!!")
    else:
        return "You need to be logged in!!"



@app.route('/getunseenmsg', methods=['GET'])
def getunseenmsg():
    if session.get('user') :
        userid = session['user']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('getunseenmsg',(userid,))
        data = cursor.fetchall()
        cursor.close()
        con.commit()
        con.close()
        return jsonify(msg=data[0][0])
    else:
        return "You need to be logged in!!"



@app.route('/mobilesignup')
def mobilesignup():
    
    return render_template('mobilesignup.html')




@app.route('/getconfirm')
def getconfirm():
    
    return render_template('getconfirm.html')





@app.route('/getconfirmationcode',methods=['GET','POST'])
def getconfirmcode():
    if request.method=='POST':
        try:
            _email = request.form['inputEmail']
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('cavail',(_email,))
            data = cursor.fetchall()
            x=int(data[0][0])
            if x == 0:
                return jsonify(msg="Sorry this email is not registered with us")
            else :

                con = mysql.connect()
                cursor = con.cursor()
                cursor.callproc('checkconfirm',(_email,))
                data = cursor.fetchall()
                y=int(data[0][0])
                if y == 1:
                    return jsonify(msg="This email is already confirmed")
                else:
                    token = ts.dumps(_email, salt='email-confirm-key')
                    message = url_for('confirm_email',token=token,_external=True)
                    html=render_template("confirmationmail.html",message=message)
                    return jsonify(msg=smail(_email,html)) 
        except Exception as e:
            return render_template('error.html',error = str(e))
        finally:
            cursor.close() 
            con.close()
    return render_template("getconfirm.html")



@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')




