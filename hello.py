from flask import Flask,render_template,session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField, TextField, IntegerField, BooleanField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
from threading import Thread
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app=Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite3')

app.config['MAIL_SERVER'] ='smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SENDER'] = 'Flask-website'
app.config['ADMIN'] = os.environ.get('ADMIN')

app.config['MAIL_SUBJECT_PREFIX'] = 'Feedback -'

db=SQLAlchemy(app)
bootstrap=Bootstrap(app)
mail = Mail(app)

def send_mail_async(app,msg):
    with app.app_context():
        mail.send(msg)

def send_mail(subject,email,template,**kwargs):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + subject, sender = email, recipients = [app.config['ADMIN']] )
    msg.body = render_template (template + '.txt',**kwargs)
    msg.html = render_template (template + '.html',**kwargs)
    thr = Thread(target=send_mail_async,args=[app,msg])
    thr.start()
    return thr

def mail_copy(subject,email,template,**kwargs):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + subject, sender = app.config['MAIL_SENDER'], recipients = [email] )
    msg.body = render_template (template + '.txt',**kwargs)
    msg.html = render_template (template + '.html',**kwargs)
    thr = Thread(target=send_mail_async,args=[app,msg])
    thr.start()
    return thr


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    subject = db.Column(db.String(50))
    message = db.Column(db.String(500))

    def __repr__(self):
        return '< User %r>' % self.username



class NameForm(FlaskForm):
    name = StringField('Name ',validators=[DataRequired()])
    email = TextField('Email ',validators=[DataRequired()])
    subject = StringField('Subject ',validators=[DataRequired()])
    message = TextAreaField('Enter Your Message',validators=[DataRequired()])
    check = BooleanField('send me the copy of mail',default=False)
    submit = SubmitField('Submit')
    


@app.route('/', methods=['GET','POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User(name=form.name.data,email=form.email.data,subject=form.subject.data,message=form.message.data)
        db.session.add(user)
        db.session.commit()
        send_mail(user.subject,user.email,'mail/new_user',user=user)
        if form.check.data is True:
            mail_copy(user.subject,user.email,'mail/new_user1',user=user)
        flash('Thank You for Your feed back!!!')
        return redirect(url_for('index'))
    return render_template('index.html',form=form)

@app.route('/user/<name>')
def user(name):
    return '<h1> hello, {} !<h1>'.format(name)
    

