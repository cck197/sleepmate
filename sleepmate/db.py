from mongoengine import connect

db = connect(db="sleepmate", host="localhost", port=27017)
