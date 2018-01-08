import json

import requests
from flask import Flask, request, Response
from playhouse.shortcuts import model_to_dict
from flask_cors import CORS

from models import *

app = Flask(__name__)
CORS(app)

# DB connect and disconnect (only once)
@app.before_request
def _db_connect():
    db.connect()

@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()


@app.route('/')
def helloworld():
    return 'Moodle Middleware running!'


@app.route('/moodles')
def moodles():
    moodlesList = []
    for moodle in  Moodles.select():
        aDict = model_to_dict(moodle)
        del aDict['token']
        moodlesList.append(aDict)
    return json.dumps(moodlesList)


@app.route('/courses', methods=['GET'])
def courses():
    moodleId = request.args.get('moodleid')
    if moodleId is None:
        return Response("{'error':'moodle required'}", status=404, mimetype='application/json')

    urlWithoutFunction2 = getMoodleURL(moodleId)
    if urlWithoutFunction2 is None:
        return Response("{'error':'moodle not found'}", status=404, mimetype='application/json')

    functionToCall = 'core_course_get_courses'
    result = requests.get(urlWithoutFunction2 + functionToCall).text

    list = []
    for course in json.loads(result):
        courseDict = {}
        courseDict['id'] = course['id']
        courseDict['shortname'] = course['shortname']
        courseDict['fullname'] = course['fullname']
        courseDict['displayname'] = course['displayname']
        list.append(courseDict)
    return json.dumps(list), 200, {'ContentType': 'application/json'}


@app.route('/coursecontents')
def coursecontents():
    moodleId = request.args.get('moodleid')
    if moodleId is None:
        return Response("{'error':'moodle required'}", status=404, mimetype='application/json')

    urlWithoutFunction2 = getMoodleURL(moodleId)
    if urlWithoutFunction2 is None:
        return Response("{'error':'moodle not found'}", status=404, mimetype='application/json')

    courseId = request.args.get('courseid')
    if courseId is None:
        return Response("{'error':'course required'}", status=404, mimetype='application/json')

    params = '&courseid=' + courseId
    functionToCall = 'core_course_get_contents'
    response = requests.get(urlWithoutFunction2 + functionToCall + params).text

    result = json.loads(response)

    if type(result) is dict and result.get('exception') is not None:
        return Response("{'error':" + result['message'] + "}", status=404, mimetype='application/json')

    return json.dumps(result), 200, {'ContentType': 'application/json'}


@app.route('/file')
def file():
    moodleId = request.args.get('moodleid')
    if moodleId is None:
        return Response("{'error':'moodle required'}", status=404, mimetype='application/json')

    moodle = Moodles.get(Moodles.moodle_id == moodleId)

    urlWithoutFunction2 = getMoodleURL(moodleId)
    if urlWithoutFunction2 is None:
        return Response("{'error':'moodle not found'}", status=404, mimetype='application/json')

    courseId = request.args.get('courseid')
    if courseId is None:
        return Response("{'error':'course required'}", status=404, mimetype='application/json')

    params = '&courseid=' + courseId
    functiontocall = 'core_course_get_contents'
    result = json.loads(requests.get(urlWithoutFunction2 + functiontocall + params).text)

    sectionid = request.args.get('sectionid')
    if sectionid is None:
        return Response("{'error':'section required'}", status=404, mimetype='application/json')
    moduleid = request.args.get('moduleid')
    if moduleid is None:
        return Response("{'error':'module required'}", status=404, mimetype='application/json')
    fileName = request.args.get('filename')
    if fileName is None:
        return Response("{'error':'filename required'}", status=404, mimetype='application/json')

    for section in result:
        if section['id'] == int(sectionid):
            for module in section['modules']:
                if module['id'] == int(moduleid):
                    for content in module['contents']:
                        if content['filename'] == fileName:
                            fileURL = content['fileurl']
                            if content['type'] != 'url':
                                fileURL += '&token=' + moodle.token
                            response = requests.get(fileURL)
                            return Response(response, status=200, content_type=response.headers._store['content-type'][1])
    print('File Not Found')
    return Response("{'error':'file not found'}", status=404, mimetype='application/json')


# Moodle URL Creator
def getMoodleURL(moodleId):
    try:
        moodle = Moodles.get(Moodles.moodle_id == moodleId)
    except Exception:
        return None
    return moodle.host + '/webservice/rest/server.php' + '?wstoken=' + moodle.token + '&moodlewsrestformat=json&wsfunction='

if __name__ == '__main__':
    app.run()