from flask import Flask, request, Response, render_template
from flask_cors import CORS
import json
import requests
import moodle_api
import util
from moodles_dao import *


app = Flask(__name__)
CORS(app)
moodles_borg = MoodlesBorg()


# HTTP error handling
@app.errorhandler(404)
def _not_found(error):
    return render_template('404.html'), 404


@app.route('/')
def _check():
    return 'Moodle Plugin running...'


# Register a new Moodle in database
@app.route('/moodle')
def _moodle():
    params_required = ['host', 'token']
    params_requested = dict(request.args)

    is_validated, response_with_error = util.validate_params(params_requested, params_required)
    if not is_validated:
        return response_with_error

    host_input = request.args.get('host')
    token_input = request.args.get('token')

    try:
        if util.token_exists(token_input):
            raise IntegrityError

        moodle_obj = Moodle(
            host=host_input,
            token=token_input
        )
        moodle_obj.save()
        
        moodles_borg.refresh_moodles()
    except IntegrityError:
        return Response("{'error': 'Token already exists'}", status=404, mimetype='application/json')
    except:
        return Response("{'error': 'Moodle not registered due to unknown error'}", status=404, mimetype='application/json')
    else:
        return Response("{'message':'Moodle registered'}", status=404, mimetype='application/json')


# All Moodles in database
@app.route('/moodles')
def _moodles():
    moodles_list = list()
    for moodle in moodles_borg.get_moodles().values():
        moodles_list.append({k:v for k,v in moodle.items() if k != 'token'})
    return json.dumps(moodles_list)


# Courses of a moodle
@app.route('/courses', methods=['GET'])
def _courses():
    params_required = ['moodleid']
    params_requested = dict(request.args)

    is_validated, response_with_error = util.validate_params(params_requested, params_required)
    if not is_validated:
        return response_with_error
    
    moodle_id = request.args.get('moodleid')
    moodle_api_service = moodle_api.COURSE_GET_COURSES
    url = util.get_moodle_url(moodle_id, moodle_api_service)

    if url is None:
        return Response("{'error':'moodle with given id not found'}", status=404, mimetype='application/json')

    resp = requests.get(url)

    course_list = []
    for course in resp.json():
        course_dict = {
            'id' : course['id'],
            'shortname' : course['shortname'],
            'fullname' : course['fullname'],
            'displayname' : course['displayname']
        }
        course_list.append(course_dict)
    return json.dumps(course_list), 200, {'ContentType': 'application/json'}


# Contents of a course from a moodle
@app.route('/coursecontents')
def _course_contents():
    params_required = ['moodleid', 'courseid']
    params_requested = dict(request.args)

    is_validated, response_with_error = util.validate_params(params_requested, params_required)
    if not is_validated:
        return response_with_error

    moodle_id = request.args.get('moodleid')
    course_id = request.args.get('courseid')
    args_for_api_service = '&courseid=' + course_id
    moodle_api_service = moodle_api.COURSE_GET_CONTENTS
    url = util.get_moodle_url(moodle_id, moodle_api_service, args_for_api_service)

    if url is None:
        return Response("{'error':'moodle with given id not found'}", status=404, mimetype='application/json')

    result = requests.get(url).json()

    if type(result) is dict and result.get('exception') is not None:
        return Response("{'error':" + result.get('message') + "}", status=404, mimetype='application/json')

    return json.dumps(result), 200, {'ContentType': 'application/json'}


# Course Search
@app.route('/coursesearch')
def _course_search():
    params_required = ['moodleid', 'criteriavalue']
    params_requested = dict(request.args)

    is_validated, response_with_error = util.validate_params(params_requested, params_required)
    if not is_validated:
        return response_with_error

    moodle_id = request.args.get('moodleid')
    criteria_value  = request.args.get('criteriavalue')
    args_for_api_service = '&criteriavalue=' + criteria_value
    args_for_api_service += '&criterianame=search'
    moodle_api_service = moodle_api.COURSE_SEARCH_COURSES
    url = util.get_moodle_url(moodle_id, moodle_api_service, args_for_api_service)

    if url is None:
        return Response("{'error':'moodle with given id not found'}", status=404, mimetype='application/json')

    result = requests.get(url).json()

    if type(result) is dict and result.get('exception') is not None:
        return Response("{'error':" + result.get('message') + "}", status=404, mimetype='application/json')

    return json.dumps(result), 200, {'ContentType': 'application/json'}


# Check updated contents from a module of a course
@app.route('/coursecheckupdates')
def _course_check_updates():
    params_required = ['moodleid', 'courseid', 'moduleid', 'since']
    params_requested = dict(request.args)

    is_validated, response_with_error = util.validate_params(params_requested, params_required)
    if not is_validated:
        return response_with_error

    moodle_id = request.args.get('moodleid')
    args_for_api_service = ''
    course_id = request.args.get('courseid')
    args_for_api_service += '&courseid=' + course_id
    module_id = request.args.get('moduleid')
    args_for_api_service += '&tocheck[0][id]=' + module_id
    since = request.args.get('since')
    args_for_api_service += '&tocheck[0][since]=' + since
    args_for_api_service += '&tocheck[0][contextlevel]=module'
    moodle_api_service = moodle_api.COURSE_CHECK_UPDATES
    url = util.get_moodle_url(moodle_id, moodle_api_service, args_for_api_service)

    if url is None:
        return Response("{'error':'moodle with given id not found'}", status=404, mimetype='application/json')

    result = requests.get(url).json()

    if type(result) is dict and result.get('exception') is not None:
        return Response("{'error':" + result.get('message') + "}", status=404, mimetype='application/json')

    return json.dumps(result), 200, {'ContentType': 'application/json'}


# Enrolled users of a course from a moodle
@app.route('/enrolledusers')
def _enrolled_users():
    params_required = ['moodleid', 'courseid']
    params_requested = dict(request.args)

    is_validated, response_with_error = util.validate_params(params_requested, params_required)
    if not is_validated:
        return response_with_error

    moodle_id = request.args.get('moodleid')
    course_id = request.args.get('courseid')
    args_for_api_service = '&courseid=' + course_id
    moodle_api_service = moodle_api.ENROL_GET_ENROLLED_USERS

    url = util.get_moodle_url(moodle_id, moodle_api_service, args_for_api_service)

    if url is None:
        return Response("{'error':'moodle with given id not found'}", status=404, mimetype='application/json')

    result = requests.get(url).json()

    if type(result) is dict and result.get('exception') is not None:
        return Response("{'error':" + result.get('message') + "}", status=404, mimetype='application/json')

    return json.dumps(result), 200, {'ContentType': 'application/json'}


# Events of a moodle
# Note: Result does not include course events because they are visible to enrolled users only.
@app.route('/events', methods=['GET'])
def _events():
    params_required = ['moodleid']
    params_requested = dict(request.args)

    is_validated, response_with_error = util.validate_params(params_requested, params_required)
    if not is_validated:
        return response_with_error

    moodle_id = request.args.get('moodleid')
    args_for_api_service = ''
    moodle_api_service = moodle_api.CALENDAR_GET_CALENDAR_EVENTS

    url = util.get_moodle_url(moodle_id, moodle_api_service, args_for_api_service)

    if url is None:
        return Response("{'error':'moodle with given id not found'}", status=404, mimetype='application/json')

    result = requests.get(url).json()
    return json.dumps(result) , 200, {'ContentType': 'application/json'}


# Accesses the file of any format in a course of a moodle
@app.route('/file')
def _file():
    params_required = ['moodleid', 'courseid', 'sectionid', 'filename']
    params_requested = dict(request.args)

    is_validated, response_with_error = util.validate_params(params_requested, params_required)
    if not is_validated:
        return response_with_error

    moodle_id = request.args.get('moodleid')
    course_id = request.args.get('courseid')
    args_for_api_service = '&courseid=' + course_id
    moodle_api_service = moodle_api.COURSE_GET_CONTENTS

    url = util.get_moodle_url(moodle_id, moodle_api_service, args_for_api_service)
    if url is None:
        return Response("{'error':'moodle with given id not found'}", status=404, mimetype='application/json')

    result = json.loads(requests.get(url).text)

    moodle = util.get_moodle_by_id(moodle_id)
    section_id = request.args.get('sectionid')
    module_id = request.args.get('moduleid')
    file_name = request.args.get('filename')

    for section in result:
        if section['id'] == int(section_id):
            for module in section['modules']:
                if module['id'] == int(module_id):
                    for content in module['contents']:
                        if content['filename'] == file_name:
                            file_url = content['fileurl']
                            if content['type'] != 'url':
                                file_url += '&token=' + moodle.get('token')
                            response = requests.get(file_url)
                            return Response(response, status=200, content_type=response.headers._store['content-type'][1])
    print('file not found')
    return Response("{'error':'file not found'}", status=404, mimetype='application/json')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
