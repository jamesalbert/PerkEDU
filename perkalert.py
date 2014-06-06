'''
Bulletin Board Admin Forwarder
=============================

send and receive messages to
and from the bulletin board.
'''

from email.mime.text import MIMEText as text
import email
import requests
import threading
import json
import smtplib
import imaplib

'''
user variables
'''
phost = 'http://secret.url'
shost = 'smtp.gmail.com'
sport = 587
user = 'nobody'
passw = 'nothing'
phone = '5555555555'


def set_interval(func, sec):
    '''
    snippet from stamat (https://gist.github.com/stamat/5371218)
    '''
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def send(msg, id):
    s = smtplib.SMTP(shost, sport)
    s.starttls()
    s.login(user, passw)

    m = text(msg)
    m['Subject'] = id
    m['From'] = user
    m['To'] = phone

    s.sendmail(user, phone, m.as_string())
    log('message has been sent...')


def last_answer(qid):
    res = requests.get('%s%s%s' % (phost, 'getquestionanswers/', qid))
    if res.status_code is not 200:
        return {'error': 'network error'}

    abody = res.json()['data'][0]
    name = abody['studentname']
    answ = abody['answer']

    return name, answ


def answ_alert(p):
    poster = p['studentname']
    question = p['question']
    date = p['modified']
    pid = p['id']
    aname, answer = last_answer(pid)

    rstr = '%s\'s question:\n\
           "%s..."\n\
           was answered by %s who said:\n\
           "%s..."\n\
           at %s'
    msg = rstr % (poster, question[:22], aname, answer[:22], date)
    send(msg, pid)


def post_alert(p):
    poster = p['studentname']
    question = p['question']
    date = p['modified']
    pid = p['id']

    rstr = '%s posted:\n\
           "%s..."\n\
           at %s'
    msg = rstr % (poster, question[:22], date)
    send(msg, pid)


def storequestions(q):
    qstr = json.dumps(q)
    qfile = open('questions', 'w')
    qfile.write(qstr)


def log(s):
    l = open('pa.log', 'a')
    l.write('%s\n' % s)


def checkdiff(questions):
    try:
        qfile = open('questions', 'r+')
        qjson = json.loads(qfile.read())
        obody = qjson['data']
        nbody = questions['data']

        log('checking for new messages and posts...')
        if len(obody) != len(nbody):
            post_alert(nbody[0])
            storequestions(questions)
            log('status: new post')
            return

        for o, n in zip(obody, nbody):
            oans = o['totanswers']
            nans = n['totanswers']
            if oans != nans:
                answ_alert(n)
                storequestions(questions)
                log('status: new message')
                return

        log('status: no new messages')
    except IOError:
        storequestions(questions)
        log('status: new questions file created.')
    except Exception as e:
        log('error: %s' % e.message)


def exec_pcmd(cmd, lid):
    payload = {'studentid': '',
               'questionid': lid,
               'answer': cmd}
    res = requests.post('%s%s' % (phost, 'postanswer'), data=payload)
    print res.text


def checkemail():
    res = str()
    m = imaplib.IMAP4_SSL('imap.gmail.com')
    m.login(user, passw)
    m.select('inbox')
    status, res = m.search(None, '(UNSEEN FROM "%s")' % phone)
    if not res[0]:
        log('no new emails...')
        return

    m.select('sent')
    status, sent = m.search(None, '(TO "%s")' % phone)
    status, last = m.fetch(sent[0].split()[0], '(RFC822)')
    lbody = email.message_from_string(last[0][1])
    lid = lbody['subject']

    for e in res[0].split():
        s, r = m.fetch(e, '(RFC822)')
        body = email.message_from_string(r[0][1])
        cmd = body['subject']
        exec_pcmd(cmd, lid)
        m.store(e, '+FLAGS', '\\Seen')

    log('you replied with "%s"' % cmd)


def refresh():
    checkemail()
    res = requests.get('%s%s' % (phost, 'getquestions'))
    if res.status_code is 200:
        checkdiff(res.json())


set_interval(refresh, 10)
