'''
Perk Utilities

random home-made functions
'''

from datetime import datetime
from subprocess import PIPE, Popen


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

            return res

        return {'status': 'query executed'}

    return wrap


def bb_dt():
    '''datetime stamp for bulletin board'''
    dt = datetime.now()
    now = dt.strftime('%Y-%m-%d %H:%M:%S')
    return now


def current_time():
    '''get current time'''
    try:
        time_now = datetime.today()
        return time_now.strftime('%I:%M:%S %m-%d-%Y')
    except (OSError, IOError) as excp:
        return {'error': excp.message}


def check_points(user):
    '''check last received point'''
    try:
        last_point = user.custom_data['last_point']
        time_now = current_time()
        last_point_dt = datetime.strptime(last_point, '%I:%M:%S %m-%d-%Y')
        time_now_dt = datetime.strptime(time_now, '%I:%M:%S %m-%d-%Y')
        current_diff = time_now_dt - last_point_dt
        minutes_passed = current_diff.seconds / 60
        if minutes_passed < 15:
            message = 'stay checked in for %d more minutes to earn more points'
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
