from utils import execute
import peewee as pw

db = 'perkedu'

database = pw.MySQLDatabase(db, **{'user': 'root'})


class UnknownField(object):
    pass


class BaseModel(pw.Model):
    class Meta:
        database = database


class Questions(BaseModel):
    anonymous = pw.IntegerField(null=True)
    answers = pw.IntegerField()
    modified = pw.DateTimeField()
    name = pw.CharField(max_length=255)
    posted = pw.DateTimeField()
    question = pw.CharField(max_length=255)
    studentid = pw.CharField(db_column='student_id', max_length=254)

    class Meta:
        db_table = 'questions'


class Answers(BaseModel):
    answer = pw.CharField(max_length=255)
    modified = pw.DateTimeField()
    name = pw.CharField(max_length=255)
    posted = pw.DateTimeField()
    questionid = pw.ForeignKeyField(db_column='question_id',
                                    rel_model=Questions)
    rating = pw.IntegerField()
    studentid = pw.CharField(db_column='student_id', max_length=254)

    class Meta:
        db_table = 'answers'


@execute
def post_question(**kwargs):
    return Questions.insert(**kwargs)


@execute
def post_answer(**kwargs):
    return Answers.insert(**kwargs)


@execute
def report_questions(id=None, *args):
    q = Questions.select()
    if id:
        return q.where(Questions.id == id)

    return q


@execute
def report_answers(id=None, qid=None, *args):
    q = Answers.select()
    if id:
        return q.where(Answers.id == id)

    if qid:
        return q.where(Answers.questionid == qid)

    return q


@execute
def edit_question(**kwargs):
    id = kwargs.pop('id')
    return Questions.update(**kwargs).where(Questions.id == id)


@execute
def edit_answer(**kwargs):
    id = kwargs.pop('id')
    return Answers.update(**kwargs).where(Answers.id == id)


@execute
def delete_question(id):
    return Questions.delete().where(Questions.id == id)


@execute
def delete_answer(id=None, qid=None):
    q = Answers.delete()
    if qid:
        return q.where(Answers.questionid == qid)

    return Answers.delete().where(Answers.id == id)
