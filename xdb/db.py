#!/bin/env python3

# -*- coding=utf-8 -*-

import pymysql

"""
This is the db model for easy use the Db operation, such as `INSERT` | `UPDATE` | `DELETE` | `SELECT`
Xdb contains these class for easy ORM use:
Xdb->Db->Model
"""


class Model(object):
    """
    This is the Db model, Model is the class to operate the table
    """

    """ _data: The model data to use for INSERT|UPDATE|DELETE|SELECT"""
    _data = {}

    """_fields: The table fields"""
    _table_fields = []

    """_fields was the fields which to fetch from the Db engine."""
    _fields = {}

    """_where was the where conditions to filter the value rows"""
    _where = {}
    _where_sql = ""

    """_group_by: the group by condition in SQL """
    _group_by = {}

    """_order_by: the order by condition in SQL """
    _order_by = {}

    """_table_name was the table name which you want to operate"""
    _table_name = ""

    """_limit list limit"""
    _limit = []

    """_executed_sql: the result sql executed by Db opearation"""
    _executed_sql = ""

    def __init__(self, db):
        """
        :param db: pymysql
        """
        self.db_object = db
        self._table_name = self.tableName()

        fields_sql = "SHOW FULL COLUMNS FROM " + self._table_name
        db = self.db_object.cursor(pymysql.cursors.DictCursor)
        db.execute(fields_sql)
        result = db.fetchall()

        for v in result:
            self._table_fields.append(v['Field'])
        # end for

    # end __init__()

    def setData(self, name, value):
        """
        To set the model data with the key
        :param name: key name
        :param value: key value
        :return: self
        """
        self._data[name] = value
        return self

    # end setData()

    def fields(self, *args, **kwargs):
        """
        To fetch the data when you want to execute the SELECT statement, kwargs will replace the args data if exists.
        :param args: Which field you want to fetch, such as: 'id', 'name', 'age
        :param kwargs: If you want to set the field's alias, you can use this fields, such as a="a.id" was a AS a.id
        :return: self
        """
        if args and len(args):
            for arg in args:
                if '.' in arg:
                    self._fields[str(arg)] = None
                else:
                    self._fields[str('`') + str(arg) + str('`')] = None

        if kwargs and len(kwargs):
            for v in kwargs:
                if '.' in v:
                    self._fields[v] = kwargs[str(v)]
                else:
                    self._fields[str('`') + str(v) + str('`')] = kwargs[str(v)]
        return self

    # end fields()

    def where(self, **kwargs):
        """
        To set the where condition if you want to filter some data rows
        kwargs support three types:
        1: { id="hello", sex=1 } ===> `id` = 'hello' AND `sex` = 1
        2: { id=[1, 2, 3, 4] }   ===> `id` IN (1, 2, 3, 4)
        3: { time={">": 10, "<": 100} } ===> time > 10 AND time < 100
        :param kwargs: key-value filters such as a=1 was the SQL: WHERE `a` = 1
        :return: self
        """
        if self._where_sql:
            self._where_sql += " AND "
        if kwargs and len(kwargs):
            cont = "AND"
            is_in = 0
            if '_xor' in kwargs:
                cont = str(kwargs.pop('_xor')).upper()
            self._where_sql += "("
            for k in kwargs:
                if '.' in k:
                    v = k
                else:
                    v = '`' + k + '`'
                # to see value is list or tuple
                if type(kwargs[k]) is list or type(kwargs[k]) is tuple:
                    self._where_sql += str(v) + " IN ("
                    for vv in kwargs[k]:
                        if type(vv) is str:
                            self._where_sql += "'" + self._addslashes(str(vv)) + "', "
                        else:
                            self._where_sql += str(vv) + ", "
                    self._where_sql = self._where_sql[0:-2]
                    self._where_sql += ')'
                    is_in = 0
                elif type(kwargs[k]) is dict:
                    # id={">": 10, "<": 20}
                    for cr in kwargs[k]:
                        self._where_sql += str(v) + " " + str(cr) + " " + str(kwargs[k][cr]) + " AND "
                    self._where_sql = self._where_sql[0:-4]
                    is_in = 0
                else:
                    if type(kwargs[k]) is str:
                        self._where[v] = "'" + kwargs[k] + "'"
                        self._where_sql += str(v) + "='" + self._addslashes(str(kwargs[k])) + "' " + str(cont) + " "
                    else:
                        self._where[v] = kwargs[k]
                        self._where_sql += str(v) + "=" + self._addslashes(str(kwargs[k])) + " " + str(cont) + " "
                    is_in = 1
            if is_in:
                self._where_sql = self._where_sql[:-(len(cont)+1)]
            self._where_sql += ")"
        return self

    # end where()

    def tableName(self):
        """
        Return the table name
        :return: string
        """
        return self.__class__.__name__

    # end tableName()

    def groupBy(self, *args, **kwargs):
        """
        To combine the group by condition
        :param args: the group by condition
        :param kwargs: the group by condition
        :return: self
        """
        if args and len(args):
            for v in args:
                if '.' in v:
                    k = v
                else:
                    k = '`' + v + '`'
                self._group_by[k] = None

        if kwargs and len(kwargs):
            for v in kwargs:
                if '.' in v:
                    k = v
                else:
                    k = '`' + v + '`'
                self._group_by[k] = kwargs[v]

        return self

    # end groupBy()

    def orderBy(self, *args, **kwargs):
        """
        To combine the order by condition
        :param args: The ORDER BY condition
        :param kwargs: The ORDER BY condition
        :return: self
        """
        if args and len(args):
            for v in args:
                if '.' in v:
                    k = v
                else:
                    k = '`' + v + '`'
                self._order_by[k] = 'DESC'
        if kwargs and len(kwargs):
            for v in kwargs:
                if '.' in v:
                    k = v
                else:
                    k = '`' + v + '`'
                self._order_by[k] = kwargs[v]
        return self

    # end orderBy()

    def limit(self, limit, offset=None):
        """
        Set the LIMIT value
        :param limit: limit
        :param offset: offset
        :return: self
        """
        if limit:
            self._limit.append(limit)
        if offset:
            if not limit:
                raise AttributeError("limit parameter must provide, if offset provided.")
            self._limit.append(offset)

        return self

    # end limit()

    def getExecutedSql(self):
        """
        Get the executed Sql
        :return: string
        """
        return self._executed_sql

    # end getExecutedSql()

    def _addslashes(self, s):
        """
        Add slashes to the string
        :param s: String which you want to add slashes to.
        :return: String contains the slashes
        """
        result = ''
        if s and len(s):
            for se in s:
                if se == '"' or se == "'":
                    result += "\\"
                result += se
            # end for
        # end if
        return result

    # end _addslashes()

    def _make_select_sql(self):
        """
        Generate the SELECT sql with the given parameters.
        :return: string The sql which need to be exeuted.
        """
        sql = "SELECT "

        if self._fields and len(self._fields):
            for field in self._fields:
                if self._fields[field]:
                    sql += str(field) + " AS " + str(self._fields[field]) + ", "
                else:
                    sql += str(field) + ', '
            sql = sql[0:-2] + " "
        else:
            sql += "* "

        if self._table_name:
            sql += "FROM " + self._table_name + " "
        else:
            raise AttributeError("tableName must return name")

        if self._where_sql:
            sql += "WHERE "
            sql += self._where_sql

        if self._group_by and len(self._group_by):
            sql += " GROUP BY "
            for g in self._group_by:
                if self._group_by[g]:
                    sql += str(g) + " " + str(self._group_by[g]) + ", "
                else:
                    sql += str(g) + ", "
            sql = sql[0:-2]

        if self._order_by and len(self._order_by):
            sql += " ORDER BY "
            for o in self._order_by:
                if self._order_by[o]:
                    sql += str(o) + " " + str(self._order_by[o]) + ", "
                else:
                    sql += str(0) + " DESC, "
            sql = sql[0:-2]

        if self._limit and len(self._limit):
            if len(self._limit) == 1:
                sql += " LIMIT " + str(self._limit[0])
            elif len(self._limit) == 2:
                sql += " LIMIT " + str(self._limit[0]) + ", " + str(self._limit[1])

        return sql

    # end _make_select_sql()

    def one(self):
        """
        Get the result from the Db engine.
        :return: dict
        """
        sql = self._make_select_sql()
        result = self.db_object.cursor(pymysql.cursors.DictCursor)
        self._executed_sql = sql
        result.execute(sql)
        return result.fetchone()

    # end one()

    def all(self):
        """
        Get all result which exists in Db engine.
        :return: dict
        """
        sql = self._make_select_sql()
        result = self.db_object.cursor(pymysql.cursors.DictCursor)
        self._executed_sql = sql
        result.execute(sql)
        return result.fetchall()

    # end all()

    def update(self, **kwargs):
        """
        UPDATE the Db data
        kwargs: { a="hello", b="world" }
        :param kwargs: which data you want to set
        :return: int number of the rows to be affected.
        """
        sql = "UPDATE " + self._table_name + " SET "

        if kwargs and len(kwargs):
            for k in kwargs:
                if str(k).find('.'):
                    if type(kwargs[k]) is int:
                        sql += '`' + str(k) + '`=' + str(kwargs[k]) + ", "
                    else:
                        sql += '`' + str(k) + "`='" + str(kwargs[k]) + "', "
            sql = sql[0:-2]

        if self._where_sql:
            sql += " WHERE " + self._where_sql
        else:
            raise AttributeError("You must set the where condition.")

        self._executed_sql = sql
        result = self.db_object.cursor()
        data = result.execute(sql)
        self.db_object.commit()
        return data

    # end update()

    def delete(self):
        """
        DELETE the Db data
        :return: The number of rows affected.
        """
        sql = "DELETE FROM " + self._table_name

        if self._where_sql:
            sql += " WHERE " + self._where_sql
        else:
            raise AttributeError("You must set the where condition.")

        self._executed_sql = sql
        result = self.db_object.cursor()
        data = result.execute(sql)
        self.db_object.commit()
        return data

    # end delete()

    def save(self, **kwargs):
        """
        INSERT INTO table with the given data
        INSERT INTO Db (`id`, `name`) VALUES(1, "hello")
        :param kwargs: The data you want to insert into.
        :return: The number of rows insert into Db
        """
        sql = "INSERT INTO " + self._table_name
        key_sql = "("
        val_sql = " VALUES("

        if kwargs and len(kwargs):

            for k in kwargs:
                if k not in self._table_fields:
                    continue
                if str(k).find('.'):
                    key_sql += str(k) + ", "
                else:
                    key_sql += "`" + str(k) + "`, "
                # end if

                if kwargs[k] is None:
                    kwargs[k] = 'NULL'
                if type(kwargs[k]) is str and kwargs[k] != 'NULL':
                    val_sql += "'" + self._addslashes(kwargs[k]) + "', "
                elif type(kwargs[k]) is str and kwargs[k] == 'NULL':
                    val_sql += self._addslashes(kwargs[k]) + ", "
                else:
                    val_sql += str(kwargs[k]) + ", "
                # end if
        else:
            raise AttributeError("You must provide data which you want to insert.")

        key_sql = key_sql[0:-2] + ")"
        val_sql = val_sql[0:-2] + ")"

        sql += key_sql + val_sql
        self._executed_sql = sql
        result = self.db_object.cursor()
        data = result.execute(sql)
        self.db_object.commit()
        return data

    # end save()

    def batchSave(self, datas):
        """
        This feature currently only support in MySQL.
        INSERT INTO table with the given data
        INSERT INTO Db (`id`, `name`) VALUES(1, "hello"),(2, "world")
        :param datas: The data you want to insert into. such as: [{"ab": "world"}, {"db": "version"}]
        :return: The number of rows insert into Db
        """
        sql = "INSERT INTO " + self._table_name
        key_sql = " ("
        val_sql = " VALUES"
        key_set = 0
        v_sql = ""

        if datas and len(datas):
            for v in datas:
                if v and type(v) is dict:
                    v_sql += "("
                    for kv in v:
                        if kv not in self._table_fields:
                            continue
                        if not key_set:
                            if str(kv).find('.'):
                                key_sql += str(kv) + ", "
                            else:
                                key_sql += "`" + str(kv) + "`, "
                            # end if
                        # end key_set
                        if v[kv] is None:
                            v[kv] = 'NULL'
                        if type(v[kv]) is str and v[kv] != 'NULL':
                            v_sql += "'" + self._addslashes(v[kv]) + "', "
                        elif type(v[kv]) is str and v[kv] == 'NULL':
                            v_sql += self._addslashes(v[kv]) + ", "
                        else:
                            v_sql += str(v[kv]) + ", "
                        # end if
                    if not key_set:
                        key_set = 1
                    if v_sql and len(v_sql):
                        v_sql = v_sql[0:-2]
                    v_sql += "), "
                    # end for
                # end if
            if v_sql and len(v_sql):
                v_sql = v_sql[0:-2]
            if key_sql and len(key_sql):
                key_sql = key_sql[0:-2] + ")"
            # end for
        else:
            raise AttributeError("You must provide data which you want to insert.")
        # end if
        sql += key_sql + val_sql + v_sql
        self._executed_sql = sql
        result = self.db_object.cursor()
        data = result.execute(sql)
        self.db_object.commit()
        return data

    # end batchSave()

    def createCommand(self, raw_sql):
        """
        This is the raw method to run the SELECT sql with the given SQL statement.
        :param raw_sql: string which sql you want to run.
        :return: The result of the SQL result.
        """
        if type(raw_sql) is not str:
            raise AttributeError("Please set raw_sql with type string.")
        result = self.db_object.cursor(pymysql.cursors.DictCursor)
        self._executed_sql = raw_sql
        result.execute(raw_sql)
        return result.fetchall()

    # end createCommand()

    def execCommand(self, raw_sql):
        """
        This is the raw method to run the UPDATE|INSERT sql with the given SQL statement.
        :param raw_sql: string which sql you want to run.
        :return: The result of the SQL result.
        """
        if type(raw_sql) is not str:
            raise AttributeError("Please set raw_sql with type string.")
        result = self.db_object.cursor()
        self._executed_sql = raw_sql
        data = result.execute(raw_sql)
        self.db_object.commit()
        return data

    # end execCommand()
# end class Model
