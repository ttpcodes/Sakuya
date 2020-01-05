from sakuya.database import mappings


def first_or_create(session, model, model_id):
    instance = session.query(model).filter_by(id=str(model_id)).first()
    if not instance:
        instance = model(id=str(model_id))
        session.add(instance)
        session.commit()
    return instance


def to_sql(session, obj, model):
    mapping = mappings[model.__name__]
    if isinstance(mapping, dict):
        attrs = mapping['parent']['attribute'].split('.')
        arg = obj
        for attr in attrs:
            arg = getattr(arg, attr)
        kwargs = {
            mapping['parent']['column']: str(arg)
        }
        sql = mapping['model']
        instance = session.query(sql).filter_by(id=str(obj.id), **kwargs).first()
        if not instance:
            first_or_create(session, mapping['parent']['model'], arg)
            if mapping.get('child'):
                first_or_create(session, mapping['child'], obj.id)
            instance = model(id=str(obj.id), **kwargs)
            session.add(instance)
            session.commit()
        return instance
    else:
        return first_or_create(session, mapping, obj.id)
