from flask import Response, json

from moodles_dao import MoodlesBorg

moodles_borg = MoodlesBorg()


# Moodle URL Creator
def get_moodle_url(moodle_id:int, function_to_call=None, params=None):
    try:
        moodle = moodles_borg.get_moodles().get(int(moodle_id))
        if moodle is None:
            raise Exception()
    except :
        return None

    host = moodle.get('host')
    end_point = '/webservice/rest/server.php'
    token = '?wstoken=' + moodle.get('token')
    rest_format = '&moodlewsrestformat=json'
    function_param = '&wsfunction=' + function_to_call

    url = host + end_point + token + rest_format

    if function_to_call is not None:
        url += function_param

    if params is not None:
        url += params

    return url


def validate_params(params_requested:dict, params_required:list=[]):
    missing_params = [r for r in params_required if r not in list(params_requested.keys())]
    if missing_params:
        error_msg = {'error': ', '.join(p for p in missing_params) + ' required'}
        return False, Response(json.dumps(error_msg), status=404, mimetype='application/json')
    else:
        return True, None


def token_exists(token):
    all_tokens = [v for m in moodles_borg.get_moodles().values() for k,v in m.items() if k == 'token']
    return token in all_tokens


def get_moodle_by_id(moodle_id):
    for m in moodles_borg.get_moodles().values():
        if m.get('moodle_id') == int(moodle_id):
            return m
    return None