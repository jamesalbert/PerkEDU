'''
Perk Utilities

random home-made functions
'''

from datetime import datetime, timedelta
from subprocess import PIPE, Popen
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto import Random
from geopy.distance import vincenty
import os
import base64


def gen_perk_code():
    '''generate a secure perk code'''
    t = os.urandom(32)
    return base64.b64encode(t)


def execute(fn):
    '''cleanly execute mysql queries'''
    def wrap(*args, **kwargs):
        q = fn(*args, **kwargs)
        db_res = q.execute()
        if 'report' in fn.__name__:
            res = {'status': ''}
            column = kwargs.get('c')
            if column:
                res['bodies'] = [{r.id: getattr(r, column)} for r in db_res]
            else:
                res['bodies'] = [r._data for r in db_res]

            res['status'] = True
            return res

        return {'status': 'query executed'}

    return wrap



def decrypt(**kwargs):
    '''decrypt gps coordinates'''
    elat = kwargs['latitude']
    elon = kwargs['longitude']
    dlat = base64.b64decode(elat)
    dlon = base64.b64decode(elon)
    return (float(dlat), float(dlon))


def check_distance(**kwargs):
    '''check distance between campus and student'''
    school = (34.00673, -118.38574)
    current = decrypt(**kwargs)
    distance = vincenty(school, current)
    return {'distance': distance.miles}


def bb_dt():
    '''datetime stamp for bulletin board'''
    dt = datetime.now()
    now = dt.strftime('%Y-%m-%d %H:%M:%S')
    return now


def current_time():
    '''get current time'''
    try:
        time_now = datetime.now()
        return time_now.strftime('%Y-%m-%d %H:%M:%S')
    except (OSError, IOError) as excp:
        return {'error': excp.message}


def int_to_days(i):
    return timedelta(i)


def sqldt_str_to_dt(s):
    return datetime.strptime(s, '%a, %d %b %Y %H:%M:%S %Z')


def str_to_dt(s):
    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')


def time_from_now(ds):
    time_now = current_time()
    time_now_dt = str_to_dt(time_now)
    ds_dt = sqldt_str_to_dt(ds)
    diff = time_now_dt - ds_dt
    return diff.seconds / 60


def check_points(user):
    '''check last received point'''
    try:
        last_point = user.custom_data['last_point']
        if last_point == '':
            return True

        time_now = current_time()
        last_point_dt = str_to_dt(last_point)
        time_now_dt = str_to_dt(time_now)
        current_diff = time_now_dt - last_point_dt
        minutes_passed = current_diff.seconds / 60
        if minutes_passed < 15:
            message = 'you are unable to earn points for %d more minutes'
            diff = 15 - int(minutes_passed)
            return {'error': message % diff}
        else:
            return True

    except (OSError, IOError) as excp:
        return {'error': excp.message}


def connected():
    '''check internet connection'''
    try:
        cmd = ['ping', 'google.com', '-c', '1']
        res = Popen(cmd, stdout=PIPE, stderr=PIPE)
        res.wait()
        out, err = res.communicate()
        res_code = res.returncode
        if err:
            raise OSError(err)

        if res_code == 0:
            return True

        return False

    except (OSError, IOError) as excp:
        return {'error': excp.message}


def check_wifi():
    '''check wifi connection'''
    try:
        cmd = ['nmcli', 'connection', 'show', 'active']
        res = Popen(cmd, stdout=PIPE, stderr=PIPE)
        res.wait()
        out, err = res.communicate()
        if err:
            raise OSError(err)

        if 'vega' in out and connected():
            return True
        elif 'vega' in out and not connected():
            return None
        else:
            return False

    except (OSError, IOError) as excp:
        return {'error': excp.message}
