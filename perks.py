from utils import execute
import peewee as pw

DB = pw.MySQLDatabase('perkedu',
                      host='localhost',
                      user='root')


"""
PerkEDU Database
"""


class UnknownField(object):
    pass


class BaseModel(pw.Model):
    class Meta:
        database = DB


class Perks(BaseModel):
    cost = pw.FloatField()
    description = pw.CharField(max_length=255)
    name = pw.CharField(max_length=50)

    class Meta:
        db_table = 'perks'


@execute
def post_perk(**kwargs):
    '''post perk to database'''
    name = kwargs['name']
    desc = kwargs['description']
    cost = kwargs['cost']
    return Perks.insert(name=name,
                        description=desc,
                        cost=cost)


@execute
def report_perk(id=None):
    '''report perk from database'''
    q = Perks.select()
    if id:
        return q.where(Perks.id == id)

    return q


@execute
def edit_perk(**kwargs):
    '''edit perk from database'''
    id = kwargs.pop('id')
    return Perks.update(**kwargs).where(Perks.id == id)


@execute
def delete_perk(id):
    '''delete perk from database'''
    return Perks.delete().where(Perks.id == id)
