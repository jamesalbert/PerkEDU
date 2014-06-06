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
