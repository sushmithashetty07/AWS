
from flask import Flask, request , jsonify,Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
import os
import re
import ast
import requests
import json
import csv
import collections
from flask_marshmallow import Marshmallow
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from flask import Flask, jsonify, request, abort,redirect, url_for, session
from flask import Flask, request, jsonify
from sqlalchemy import and_, or_, not_
from sqlalchemy import update
import datetime


app=Flask(__name__)
basedir= os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)
ma=Marshmallow(app)

class User(db.Model):
        __tablename__ ='User'
        id = db.Column(db.Integer,primary_key=True)
        username=db.Column(db.String(25),unique=True)
        password=db.Column(db.String(40),unique=True)

        def __init__(self,username,password):
                self.username=username
                self.password=password

class UserSchema(ma.Schema):
        class Meta:
                fields=('id','username','password')

user_schema=UserSchema()
users_schema=UserSchema(many=True)

class Ride(db.Model):
        __tablename__='Ride'
        rideId = db.Column(db.Integer,primary_key=True)
        created_by=db.Column(db.String(25))
        source=db.Column(db.String(50))
        destination=db.Column(db.String(50))
        timestamp=db.Column(db.String(50))
        users=db.Column(db.String(500))

        def __init__(self,created_by,timestamp,source,destination,users):
                self.created_by=created_by
                self.timestamp=timestamp
                self.source=source
                self.destination=destination
                self.users=users

class RideSchema(ma.Schema):
        class Meta:
                fields=('rideId','created_by','timestamp','source','destination','users')

ride_schema=RideSchema()
rides_schema=RideSchema(many=True)

@app.route('/api/v1/users',methods=['PUT'])
def addUser():
        if request.method=='PUT':
                username=request.json['username']
                password=request.json['password']
                Exists = db.session.query(User).filter_by(username=username)

                if (Exists.scalar() is not None ):
                    data = {'message': 'user exists'}
                    return jsonify(data), 400
                else:
                    length = len(password)
                    if (length <= 10):
                            reg = r'[a-f]+'
                            m = re.match(reg,password)
                            if m:
                                data = {'message': 'password error'}
                                return jsonify(data), 409
                            new_product = User(username,password)

                            db.session.add(new_product)
                            db.session.commit()

                            data = {'message': 'user added'}
                            return jsonify(data)
                    else:
                            data = {'message': 'password length exceeded'}
                            return jsonify(data), 400
        else:
                data = {'message': 'bad request'}
                return jsonify(data), 400

@app.route('/api/v1/ride',methods=['PUT'])
def addRide():
        if request.method=='PUT':
                created_by=request.json['created_by']
                source=request.json['source']
                destination=request.json['destination']
                users=request.json['users']
                timestamp = str(datetime.datetime.now())
                new_ride = Ride(created_by,timestamp,source,destination,users)
                db.session.add(new_ride)
                db.session.commit()
                data = {'message': 'Ride added'}
                return jsonify(data)

        else:
                data = {'message': 'bad request  please check your request'}
                return jsonify(data), 400

@app.route('/api/v1/db/write',methods=['POST'])
def writetodb():
        req=request.get_json()
        table=req['table']
        method=req['method']
        if (table=="Ride" and method=="post"):
                created_by=req['created_by']
                timestamp=req['timestamp']
                source=req['source']
                destination=req['destination']
                users=req['users']
                newRide=Ride(created_by,timestamp,source,destination,users)
                db.session.add(newRide)
                db.session.commit()
                return Response(status=201)
        elif (table=="User" and method=="put"):
                username=req['username']
                password=req['password']

                newUser=User(username,password)
                db.session.add(newUser)
                db.session.commit()
                return Response(status=201)
        elif (table=="User" and method=="delete"):
                #print("hi")
                username=req['username']
                user = User.query.filter_by(username=username).first_or_404()
                db.session.delete(user)
                db.session.commit()
                return Response(status=200)
        elif(table=="Ride" and method=="delete"):
                ride_Id=req['rideId']
                ri=Ride.query.get(ride_Id)
                db.session.delete(ri)
                db.session.commit()
                #return user_schema.jsonify()
                return Response(status=200)
        else:
                return {'status_code': status.HTTP_500_BAD_GATEWAY}

@app.route('/api/v1/users', methods = ['GET'])
def usernameDisplay():

        if request.method=='GET':
                users=[]
                all_users=User.query.all()
                result=users_schema.dump(all_users)
                for user in result[0]:
                    users.append(user['username'])
                return jsonify(users), 200

        else:
                return Response(status=405)

@app.route('/api/v1/rides',methods=['GET'])
def rideDisplay():

        if request.method=='GET':
                rides= []
                all_rides=Ride.query.all()
                result=rides_schema.dump(all_rides)
                for ride in result[0]:
                    rides.append(ride)
                return jsonify(rides), 200

        else:
                return Response(status=405)

@app.route('/api/v1/rides/<rideId>',methods=['DELETE'])
def deleteRide(rideId):
    if request.method=='DELETE':
        Exists = db.session.query(Ride).filter_by(rideId=rideId)
        if (Exists.scalar() is not None):
            rideId=int(rideId)
            ri=Ride.query.get(rideId)
                db.session.delete(ri)
                db.session.commit()
            return Response(status=200)
        else:
            return Response(status=400)
    else:
        return Response(status=405)

@app.route('/api/v1/user/<userName>',methods=['DELETE'])
def deleteUser(userName):
        if request.method=='DELETE':
                Exists = db.session.query(User).filter_by(username=userName)
                if (Exists.scalar() is not None):
                        userName=str(userName)
                        ri=User.query.filter_by(username=userName).first_or_404()
                        db.session.delete(ri)
                        db.session.commit()
                        return Response(status=200)
                else:
                        return Response(status=400)
        else:
                return Response(status=405)

if __name__=='__main__':
        app.run(debug=True)
