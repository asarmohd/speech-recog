from app import app, routes, transcribe
import os
from flask import Flask, flash, request, redirect, url_for, abort, jsonify
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson import json_util, ObjectId, Binary
from datetime import datetime

# ********************************************
# Mongo DB connection functions
# ********************************************

def prepareResponse(data):
    res = { 'result': data }
    return json_util.dumps(res)

def retrieve(email):
    data = routes.recordingsCollection.find()
    if routes.recordingsCollection.count() == 0:
        data = "no data"
    return prepareResponse(data)
    

@app.route('/insert', methods=['POST'])
def insert():
   newCollectionId = routes.recordingsCollection.insert_one(request.json)
   newData = routes.recordingsCollection.find_one({'_id': newCollectionId.inserted_id})
   return prepareResponse(newData)

def pushToDatabase(fileName, email, userPermission):
    absolutePath = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], fileName))

    # Remove Commenting of the below lines once google cloud api is up and running
    # and remove lines 39 & 40 (duration and text)
    # response = transcribe.transcribe_file(absolutePath)
    # duration = response[0]
    # text = response[1]
    # temp
    duration = 10
    text = 'test test'
    # temp

    # uses ffmpeg to encode and save audio files to proper wave format
    transcribe.encodeAndSaveWAVFile(absolutePath)

    monoFilePath = fileName.split('.')[0] + '__mono.wav'
    monoAbsolutePath = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], monoFilePath))
    dateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    obj = {
        'fileName': fileName,
        'stereoFilePath': absolutePath,
        'monoFilePath': monoAbsolutePath,
        'duration_milliseconds': duration,
        'text': text,
        'timeStamp': datetime.now().strftime("%Y%m%d-%H%M%S"),
        'date': datetime.now().strftime("%d/%m/%Y"),
        'time': datetime.now().strftime("%H:%M:%S"),
        'ISOdate': datetime.strptime(dateTime, "%Y-%m-%dT%H:%M:%S.000Z"),
        'type': 'audio/wav',
        'user': routes.usersCollection.find_one({'email': email}),
        'permission': userPermission
    }
    newCollectionId = routes.recordingsCollection.insert_one(obj)
    newData = routes.recordingsCollection.find_one({'_id': newCollectionId.inserted_id})
    return prepareResponse(newData)

def existInDatabase(fileName):
    data = routes.recordingsCollection.find({'fileName': fileName})
    return data and data.count() > 0

if __name__ == 'app.auth':
    app.secret_key = 'speechSecret'
    app.run(debug=True)