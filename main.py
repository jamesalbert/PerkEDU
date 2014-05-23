'''
PerkEDU
Web app for keeping kids in school by allowing
them to earn points for being on campus which they
can use to redeem rewards.
'''

from flask import Flask, jsonify, request
from flask.ext.stormpath import StormpathManager, login_required, user
from subprocess import Popen, PIPE
from datetime import datetime
from os import environ
from peewee import *
import json

APP = Flask(__name__)
APP.config['SECRET_KEY'] = environ.get('PESK')
APP.config['STORMPATH_API_KEY_FILE'] = environ.get('PEAKFILE')
APP.config['STORMPATH_APPLICATION'] = 'PerkEDU'
APP.config['STORMPATH_ENABLE_FACEBOOK'] = True
APP.config['STORMPATH_SOCIAL'] = {
    'FACEBOOK': {
        'app_id': environ.get('PEFAK'),
        'app_secret': environ.get('PEFAS'),
    }
}

SPM = StormpathManager(APP)
DB = MySQLDatabase('perkedu',
                   host='localhost',
                   user='root')


"""
PerkEDU Database
"""


class UnknownField(object):
    pass


class BaseModel(Model):
    class Meta:
        database = DB


class Perks(BaseModel):
    cost = FloatField()
    description = CharField(max_length=255)
    name = CharField(max_length=50)

    class Meta:
        db_table = 'perks'


@APP.route('/addperk', methods=['POST'])
@login_required
def addperk():
    '''add perk to database'''
    try:
        payload = json.loads(request.data)
        name = payload['name']
        desc = payload['description']
        cost = payload['cost']
        pquery = Perks.insert(name=name,
                              description=desc,
                              cost=cost)
        pquery.execute()
        return jsonify({'status': 'perk added'})

    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})


"""
Native Functions
"""


def current_time():
    '''get current time'''
    try:
        time_now = datetime.today()
        return time_now.strftime('%I:%M:%S %m-%d-%Y')
    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})


def check_points():
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
        return jsonify({'error': excp.message})


@APP.errorhandler(500)
def fivehundred(excp):
    '''handle general 500 errors'''
    return excp.message

"""
POST Routes
"""


@APP.route('/checkin', methods=['POST'])
@login_required
def checkin():
    '''checkin to campus'''
    try:
        cust = user.custom_data
        if cust['checked_in']:
            return jsonify({'status': 'you are already checked in'})

        else:
            check_res = check_points()
            if isinstance(check_res, dict):
                return jsonify(check_res)

        if 'points' not in cust:
            user.custom_data['points'] = 100

        if check_wifi():
            user.custom_data['checked_in'] = True
            user.custom_data['points'] += 10
            user.custom_data['last_point'] = current_time()
            return jsonify({'status': 'you are now checked into campus'})

        return jsonify({'error': 'not logged into school wifi'})

    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})

    finally:
        user.custom_data.save()


@APP.route('/checkup', methods=['POST'])
@login_required
def checkup():
    '''earn two more points for staying on campus'''
    try:
        if not user.custom_data['checked_in']:
            return jsonify({'error': 'you are not checked in'})

        check_res = check_points()
        if isinstance(check_res, dict):
            return jsonify(check_res)

        if check_wifi():
            user.custom_data['last_point'] = current_time()
            user.custom_data['points'] += 2
            name = user.given_name
            return jsonify({'status': '%s just earned two more points' % name})
        else:
            return jsonify({'error': 'not logged into school wifi'})

    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})

    finally:
        user.custom_data.save()


@APP.route('/checkout', methods=['POST'])
@login_required
def checkout():
    '''checkout of campus'''
    try:
        if not user.custom_data['checked_in']:
            return jsonify({'error': 'you are already checked out.'})

        user.custom_data['checked_in'] = False
        return jsonify({'status': 'you are now checked out of campus'})

    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})

    finally:
        user.custom_data.save()


@APP.route('/useperk', methods=['POST'])
@login_required
def useperk():
    '''use perk, deactivating it for further use'''
    try:
        payload = json.loads(request.data)
        id = str(payload['id'])
        cust = user.custom_data
        if id not in cust['perks']:
            return jsonify({'error': 'you do not have this perk'})

        name = user.full_name
        pname = cust['perks'][id]['name']
        if not cust['perks'][id]['active']:
            return jsonify({'error': 'this perk has been used or expired'})

        user.custom_data['perks'][id]['active'] = False
        return jsonify({'status': '%s just used %s' % (name, pname)})

    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})

    finally:
        user.custom_data.save()


@APP.route('/redeem', methods=['POST'])
@login_required
def redeem():
    '''redeem specified perk'''
    try:
        if 'perks' not in user.custom_data:
            user.custom_data['perks'] = {}

        payload = json.loads(request.data)
        perk = Perks.get(Perks.id == payload['id'])

        if perk.id in user.custom_data['perks']:
            return jsonify({'error': 'perk already redeemed and active'})
        if user.custom_data['points'] < perk.cost:
            return jsonify({'error': 'insufficient funds'})

        user.custom_data['points'] -= perk.cost
        user.custom_data['perks'][perk.id] = {
            'name': perk.name,
            'description': perk.description,
            'cost': perk.cost,
            'active': True
        }
        return jsonify({'status': 'perk redeemed successfully'})

    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})

    finally:
        user.custom_data.save()


"""
GET Routes
"""


@APP.route('/', methods=['GET'])
@login_required
def main():
    '''main page'''
    try:
        name = user.given_name
        return jsonify({'status': 'logged in as %s' % name})
    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})


@APP.route('/profile', methods=['GET'])
@login_required
def profile():
    '''get user profile info'''
    try:
        cust = user.custom_data
        ret = {'name': user.full_name,
               'points': cust['points'],
               'checked_in_status': cust['checked_in'],
               'email': user.email,
               'username': user.username,
               'status': user.status}
        print dir(user)
        return jsonify(ret)
    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})


@APP.route('/points', methods=['GET'])
@login_required
def points():
    '''get current point count'''
    try:
        name = user.given_name
        pnt_total = user.custom_data['points']
        return jsonify({'status': '%s has %s points' % (name, pnt_total)})

    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})


@APP.route('/checkstat', methods=['GET'])
@login_required
def checkstat():
    '''get current checkin status'''
    return jsonify({'status': user.custom_data['checked_in']})


@APP.route('/myperks', methods=['GET'])
@login_required
def myperks():
    '''obtain all redeemed perks'''
    try:
        cust = user.custom_data
        return jsonify({'status': cust['perks']})
    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})


if __name__ == '__main__':
    APP.run()
