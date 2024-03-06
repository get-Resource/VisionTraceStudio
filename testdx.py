from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String,future
from pydantic import AnyHttpUrl, ConfigDict, Field, HttpUrl, PostgresDsn, validator
import sqlalchemy
Dsn = PostgresDsn.build(
            scheme="postgresql",
            username="root",
            password="root@123",
            host="127.0.0.1",
            path=f"db",
        ).unicode_string()
# 创建数据库引擎
engine = create_engine(Dsn, echo=True)
print(engine)
# 创建元数据对象
metadata = MetaData()

# 创建临时表
temp_table = Table(
    'temp_table', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50))
)
# 创建表格
metadata.create_all(engine)
# 创建连接
conn = engine.connect()

# print(temp_table.insert(),11)
# 向临时表中插入数据
conn.execute("CREATE TEMP TABLE temp_table (id INT PRIMARY KEY, name VARCHAR(255));")
conn.execute("INSERT INTO temp_table (id, name) VALUES (%(id)s, %(name)s)", [{'id': 1, 'name': '张三'}, {'id': 2, 'name': '李四'}])
a :sqlalchemy.engine.cursor.LegacyCursorResult= conn.execute("SELECT * FROM temp_table;")
print(a.fetchall(),123)
conn.execute("DROP TABLE IF EXISTS temp_table;")
# # 查询临时表中的数据
# result = conn.execute(temp_table.select())
# for row in result:
#     print(row)
# temp_table.drop()
# 删除临时表
# metadata.drop_all(engine)
