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
import bulletin
import perks
import json

APP = Flask(__name__)
APP.config['SECRET_KEY'] = "2UXM8ESTB1MVPEO8DOBFDVMBE"  # environ.get('PESK')
APP.config['STORMPATH_API_KEY_FILE'] = "/home/jbert/.stormpath/apiKey.properties"  # environ.get('PEAKFILE')
APP.config['STORMPATH_APPLICATION'] = 'PerkEDU'
APP.config['STORMPATH_ENABLE_FACEBOOK'] = True
APP.config['STORMPATH_SOCIAL'] = {
    'FACEBOOK': {
        'app_id': "691041867600496",  # environ.get('PEFAK'),
        'app_secret': "2ddc7a5e61d2cc67d3b0b3fd41c962e9"  # environ.get('PEFAS'),
    }
}

SPM = StormpathManager(APP)

"""
 Perks CRUD
"""


@APP.route('/postperk', methods=['POST'])
@login_required
def postperk():
    '''post perk to database'''
    try:
        payload = json.loads(request.data)
        perks.post_perk(**payload)
        return jsonify({'status': 'perk posted'})
    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})


@APP.route('/reportperks', defaults={'id': None}, methods=['GET'])
@APP.route('/reportperk/<int:id>')
@login_required
def reportperks(id):
    '''report perk from database'''
    try:
        res = perks.report_perk(id)
        return jsonify(res)

    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})


@APP.route('/editperk', methods=['PUT'])
@login_required
def editperk():
    '''edit perk from database'''
    try:
        payload = json.loads(request.data)

        perks.edit_perk(**payload)
        return jsonify({'status': 'perk edited'})

    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})


@APP.route('/deleteperk/<int:id>', methods=['DELETE'])
@login_required
def deleteperk(id):
    '''delete perk from database'''
    try:
        perks.delete_perk(id)
        return jsonify({'status': 'perk deleted'})

    except (OSError, IOError) as excp:
        return jsonify({'error': excp.message})

"""
Native Functions
"""


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
 Bulletin Board CRUD
"""


@APP.route('/postquestion', methods=['POST'])
@login_required
def postquestion():
    '''post question to bulletin board'''
    try:
        now = bb_dt()
        payload = json.loads(request.data)
        payload['modified'] = now
        payload['posted'] = now
        payload['answers'] = 0
        payload['studentid'] = user.email
        payload['name'] = user.full_name
        bulletin.post_question(**payload)
        return jsonify({'status': 'question posted'})
    except Exception as e:
        return jsonify({'error': e.message})


@APP.route('/postanswer', methods=['POST'])
@login_required
def postanswer():
    '''post answer to bulletin board'''
    try:
        now = bb_dt()
        payload = json.loads(request.data)
        payload['modified'] = now
        payload['posted'] = now
        payload['studentid'] = user.email
        payload['name'] = user.full_name
        payload['rating'] = 0
        question = bulletin.report_questions(id=payload['questionid'])
        answers = question['bodies'][0]['answers']
        bulletin.post_answer(**payload)
        bulletin.edit_question(**{'answers': answers+1,
                                  'id': payload['questionid']})
        return jsonify({'status': 'answer posted'})
    except Exception as e:
        return jsonify({'error': e.message})


@APP.route('/reportquestions', methods=['GET'])
@login_required
def postquestions():
    '''report questions from bulletin board'''
    try:
        questions = bulletin.report_questions()
        return jsonify({'status': questions['bodies']})
    except Exception as e:
        return jsonify({'error': e.message})


@APP.route('/reportanswers', defaults={'qid': None}, methods=['GET'])
@APP.route('/reportanswers/<int:qid>')
@login_required
def postanswers(qid):
    '''report answers from bulletin board'''
    try:
        answers = bulletin.report_answers(qid=qid)
        return jsonify({'status': answers['bodies']})
    except Exception as e:
        return jsonify({'error': e.message})


@APP.route('/editquestion', methods=['PUT'])
@login_required
def editquestion():
    '''edit questions from bulletin board'''
    try:
        now = bb_dt()
        payload = json.loads(request.database)

        if user.email != payload.pop('studentid'):
            return jsonify({'status': 'you can\'t edit questions that aren\'t yours.'})

        payload['modified'] = now
        bulletin.edit_question(**payload)
        return jsonify({'status': 'question has been modified'})
    except Exception as e:
        return jsonify({'error': e.message})


@APP.route('/editanswer', methods=['PUT'])
@login_required
def editanswer():
    '''edit answers from bulletin board'''
    try:
        now = bb_dt()
        payload = json.loads(request.data)

        if user.email != payload.pop('studentid'):
            return jsonify({'status': 'you can\'t edit answers that aren\'t yours.'})

        payload['modified'] = now
        bulletin.edit_answer(**payload)
        return jsonify({'status': 'answer has been modified'})
    except Exception as e:
        return jsonify({'error': e.message})


@APP.route('/deletequestion', methods=['DELETE'])
@login_required
def deletequestion():
    '''delete questions from bulletin board'''
    try:
        payload = json.loads(request.data)

        if user.email != payload.pop('studentid'):
            return jsonify({'status': 'you can\'t delete questions that aren\'t yours.'})

        id = payload['id']
        bulletin.delete_answer(qid=id)
        bulletin.delete_question(id)
        return jsonify({'status': 'question deleted'})
    except Exception as e:
        return jsonify({'error': e.message})


@APP.route('/deleteanswer', methods=['DELETE'])
@login_required
def deleteanswer():
    '''delete answers from bulletin board'''
    try:
        payload = json.loads(request.data)

        if user.email != payload.pop('studentid'):
            return jsonify({'status': 'you can\'t delete answers that aren\'t yours.'})

        id = payload['id']
        bulletin.delete_answer(id)
        return jsonify({'status': 'answer deleted'})
    except Exception as e:
        return jsonify({'error': e.message})


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


@APP.route('/ping', methods=['GET'])
def ping():
    '''test ping'''
    return jsonify({'status': True})


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
    APP.run(host="0.0.0.0", port=80)
