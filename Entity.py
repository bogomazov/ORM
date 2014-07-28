import psycopg2
import psycopg2.extras
import copy


class AttributError(Exception):
    pass


class Entity(object):
    db = psycopg2.connect(database='test', user='andrey', password='')

    __delete_query    = 'DELETE FROM "{table}" WHERE {table}_id=%s'
    __insert_query    = 'INSERT INTO "{table}" ({columns}) VALUES ({placeholders}) RETURNING {table}_id'
    __list_query      = 'SELECT * FROM "{table}"'
    __parent_query    = 'SELECT * FROM "{table}" WHERE {parent}_id=%s'
    __select_query    = 'SELECT * FROM "{table}" WHERE {table}_id=%s'
    __sibling_query   = 'SELECT * FROM "{sibling}" NATURAL JOIN "{join_table}" WHERE {table}_id=%s'
    __update_children = 'UPDATE "{table}" SET {parent}_id=%s WHERE {table}_id IN ({children})'
    __update_query    = 'UPDATE "{table}" SET {columns} WHERE {table}_id=%s'

    def __init__(self, id=None):
        if self.__class__.db is None:
            raise DatabaseError()

        self.__cursor = self.__class__.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.__fields = {}
        self.__loaded = False
        self.__modified = False
        self.__id     = id
        self.__table  = self.__class__.__name__.lower()

    def __getattr__(self, name):
        # check, if current instance has a quieryed attribute in its fields list.
        # load data from database and store retained data as instance fields, if needed.
        if name in self.__class__._fields:
            return self._get_column(name)
        elif name in self.__class__._parents:
            return self._get_parent(name)
        elif name in self.__class__._children:
            return self._get_children(name)
        elif name in self.__class__._siblings:
            return self._get_siblings(name)
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in self.__class__._fields:
            self.__fields[name] = value
            self.__loaded = False
            self.__modified = True
        else:
            super(Entity, self).__setattr__(name, value)

    def __insert(self):
        # insert instance data into database, and fetches table's id
        columns       = ', '.join(field for field in self.__fields)
        place_holders = ', '.join('\'{}\''.format(i) for i in self.__fields)
        self.__cursor.execute(Entity.__insert_query.format(table=self.__table, columns=columns, placeholders=place_holders))
        self.__id = self.__cursor.fetchone()[self.__table+"_id"]

    def __load(self):
        # select instance data from database, if current instance is not loaded yet.
        if self.__loaded:
            return
        self.__cursor.execute(Entity.__select_query.format(table=self.__table), [self.id])
        self.__fields = dict(self.__cursor.fetchone())
        self.__loaded  = True
        self.__modified = False

    def __update(self):
        # make an update of existing row in database
        if not self.__modified:
            return
        columns  = ', '.join('{0} = \'{1}\''.format(field, key) for field, key in self.__fields.items())
        self.__cursor.execute(Entity.__update_query.format(table=self.__table, columns=columns), self.id) 

    def _get_column(self, name):
        # return a prepared_queryed field by key.
        self.__load()
        return self.__fields[self.__table+'_'+name]

    def _get_children(self, name):
        # return an array of child entity instances
        # each child instance must have an id and be filled with data
        import models
        children = set()
        name = self._children[name]
        cls = getattr(models, name)

        self.__cursor.execute(Entity.__parent_query.format(table=name.lower(), parent=self.__table), [self.id])
        for row in self.__cursor.fetchall():
            yield cls.__row_to_instance(row)
    def _get_parent(self, name):
        # get parent id from fields with <name>_id as a key
        # return an instance of parent entity class with an appropriate id
        import models 
        cls = getattr(models, name.title())

        return cls(self.__fields[name+'_id'])

    def _get_siblings(self, name):
        # get parent id from fields with <name>_id as a key
        # return an array of sibling entity instances
        # each sibling instance must have an id and be filled with data
        import models
        name = self._siblings[name]
        cls = getattr(models, name)
        name = name.lower()
        join_table = '__'.join(sorted([name, self.__table]))

        self.__cursor.execute(Entity.__sibling_query.format(sibling=name, join_table=join_table, table=self.__table), [self.id])
        for row in self.__cursor.fetchall():
            yield cls.__row_to_instance(row)

    def _set_column(self, name, value):
        # save new attribute value in instance fields
        self.__fields['{}_{}'.format(self.__tablename, name)] = value

    @classmethod
    def __row_to_instance(cls, row):
        # construct new instance and fill its fields with row data
        instance = cls()
        instance.__fields = dict(row)
        instance.__id = row['{}_id'.format(instance.__table)]
        instance.__loaded = True
        return instance 

    @classmethod
    def __get_class_name(self, name):
        if name[len(name)-3:len(name)] == 'ies':
            return name[:len(name)-4] + 'y'
        return name[:len(name)-1]
 
    @classmethod
    def all(cls):
        # select all rows from database and construct Entity subclass
        # instance filled with row data for each row in result set.
        subclass     = set()
        new_instance = cls()

        new_instance.__cursor.execute(__list_query.format(table=cls.__name__.lower()))
        for row in new_instance.__cursor.fetchall():
            subclass.add(new_instance.__row_to_instance(row))
        
        return subclass

    def delete(self):
        # delete a row, representing current instance, from database
        self.__class__.cursor.execute(__delete_query.format(table=self.__table), [self.id])

    @property
    def id(self):
        return self.__id

    def save(self):
        # make an insert or update depending on instance id
        if self.id is None:
            self.__insert()
        else:
            self.__update()

