#!/usr/bin/env python

import sys
import urllib2
import xmltodict

from flask import Flask, make_response, jsonify, render_template, request, flash, abort, redirect

from sqlalchemy import create_engine, func, and_, exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import TextField, validators, SubmitField, BooleanField

import sakidb
from engineconfig import cstring

sys.stdout = sys.stderr

app = Flask(__name__)
Bootstrap(app)
app.debug = True

@app.route('/current')
def status():
	engine = create_engine(cstring, pool_recycle=3600)
	Session = sessionmaker(bind=engine)  # autocommit=True)
	session = Session()
	file = urllib2.urlopen('http://radioparadise.com/xml/now.xml')
	data = file.read()
	file.close()
	document = xmltodict.parse(data)
	song = document['playlist']['song'] #fetch the XML root
	print "Artist:{0}\n\rAlbum:{1}\n\rSong:{2}\n\r---".format(song['artist'],song['album'],song['title']) 
	dte = sakidb.Radio(artist=song['artist'], album=song['album'], song=song['title'])
	session.add(dte)
	try:
		session.commit()
	except exc.SQLAlchemyError:
		print "SQL Error"
	vals = session.query(sakidb.Radio).order_by(sakidb.Radio.timestamp.desc()).limit(12)
	print vals
	session.close()
	return render_template('current.html', vals=vals)



app.secret_key = "\xcd\x1f\xc6O\x04\x18\x0eFN\xf9\x0c,\xfb4{''<\x9b\xfc\x08\x87\xe9\x13"

#@app.after_request
#def session_commit(response):
#    session.commit()
#    return response

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
