##### xdb.db.Model

**xdb.db.Model** 是一个 Python 的 数据库模型操作类库，适合在简易爬虫中使用，无需进行SQL的手动拼接。

### APIs

1. **tableName() -> string**

   返回需要操作的数据库表的名称，如果不重写本方法，那么模型自动操作模型对应的数据表名(区分大小写)，如果重写 **tableName()** 函数，那么必须返回数据表名，否则报错。

2. **fields(args) -> self**

   设置模型返回的字段结构，如果调用本方法设置字段，默认返回所有字段，支持两种模式参数设置：

   - fields("id", "name", "age")

     设置 模型返回 `id` `name` `age` 字段:

     SELECT `id`, `name`, `age` FROM xxx

   - fields(id="s.id", name="sname")

     本方法设置字段的别名相当于： SELECT `id ` AS s.id `name` AS sname FROM xxx

   - fields("id", time="开始时间") 两种模式混用

     SELECT `id`, `time` AS '开始时间' FROM xxx

3. **where(args) -> self**

   设置 SQL的 WHERE 条件，如下三种模式：

   - where(id=1, sex=2)

     WHERE `id` = 1 AND `sex` = 2

   - where(id=[1, 2, 3, 4 ,5])

     WHERE `id` IN (1, 2, 3, 4, 5)

   - where(id={">":1, "<=":100})

     WHERE `id` > 1 AND `id` <= 100
   - where() 条件包含一个 `_xor` 参数用来指定链接条件，如
   　
     where(id=2, age=[22, 23], _xor="OR")
     相当于　WHERE `id` = 2 OR `age` IN (22, 23)

4. **groupBy(args) -> self**

   设置 GROUP BY 语句

   - groupBy("id", "age")

     GROUP BY `id`, `age`

5. **orderBy(args) -> self**

   设置 ORDER BY 语句

   - orderBy(id="DESC", age="ASC")

     ORDER BY `id` DESC, `age` ASC

   - orderBy("id", "age")

     不传入 DESC 或者 ASC 的情况下，默认是 DESC 排序

     ORDER BY `id` DESC, `age` ASC

6. **limit(limit, offset) -> self**

   设置 LIMIT 语句

   - limit(10, 2)

     LIMIT 10, 2

   - limit(10)

     LIMIT 10

7. **one() -> dict**

   获取一条记录，返回的类型是字典类型

8. **all() -> array**

   获取所有的记录，返回的是包含字典的数组类型

9. **update(args) -> int**

   更新某一个或者多个字段值，必须协同 **where()**方法使用，如：

   user->where(id=1)->update(name="xx")

10. **delete() -> int**

    删除某一条或者多条记录，必须协同 **where()**方法使用，如：

    user->where(id=[1,2,3])->delete()

11. **save(args) -> int**

    新增数据，如下：

    user->save(id=1, name="xdb", version="2.1")

12. **batchSave(args) -> int**

    批量插入功能，仅支持 MySQL数据库

    data = [{"id": 1, "name": "db"}, {"id": 2, "name": "vet"}]

    user->batchSave(**data)

13. **createCommand(sql) -> array**

    执行原生SQL的查找功能，如：

    createCommand("SELECT * FROM user")

14. **execCommand(sql) -> int**

    执行原生SQL的删除与更新操作， 如：

    execCommand(" UPDATE user SET name='DB' WHERE id=2")

操作demo如下：

```
import xdb.db
import pymysql

class User(xdb.db.Model):
	def tableName(self):
		""" 
		模型中需要重写本方法来告诉核心需要操作的表，如下表示User模型操作user表
		如果用户不重写本方法，那么User模型类自动操作数据库的User表(模型名称)区分大小写
        """
		return 'user'

con = pymysql.connect(host="localhost", user="root", password="3333", database="test")

# 传入 con 连接到模型即可
user = User(con)

# 获取所有的记录
print(user->all())

# 获取一条记录
print(user->one())

# 根据id逆排
print(user->orderBy(id="DESC")->all())

# 获取id等于1、2、3、4的记录
print(user->where(id=[1,2,3,4])->all())

# 获取id大于5并且小于等于100的记录
print(user->where(id={">": 5, "<=": 100})->all())

# 复杂情况
# 获取id大于2小于1000或者name等于"Josin"的用户
print(user->where(name="Josin", id={">": 2, "<": 1000}, _xor="or")->all())

# 更新记录
# 将id等于1记录中的name更改为Josin
print(user->where(id=1)->update(name="Josin"))

# 删除记录
# 删除id等于1的记录
print(user->where(id=1)->delete())

# 添加记录
print(user->save(id=1, name="Josin", time="2019-02-20 10:20:30"))

# 批量添加
data = [
    {"id": 1, "name": "Josin", "time": "2-10-02-20 10:20:30"},
    {"id": 2, "name": "XDB", "time": "2-10-02-20 10:20:31"},
]
print(user->batchSave(data))

# 执行原生SQL
# 查询语句
print(user->createCommand("SELECT * FROM user"))

# 更新与删除语句
print(user->execCommand("UPDATE user SET name='Josin' WHERE id = 1"))

```

