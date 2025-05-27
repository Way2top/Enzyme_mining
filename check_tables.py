import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enzyme_2.settings')
django.setup()

import MySQLdb
from django.conf import settings

# 连接数据库
conn = MySQLdb.connect(
    host=settings.DATABASES['default']['HOST'],
    port=int(settings.DATABASES['default']['PORT']),
    user=settings.DATABASES['default']['USER'],
    passwd=settings.DATABASES['default']['PASSWORD'],
    db=settings.DATABASES['default']['NAME']
)

cursor = conn.cursor()

# 需要检查的表
tables = [
    'protein_basic_info',
    'protein_structure_info',
    'protein_subcellular_location',
    'protein_function_annotation',
    'protein_comprehensive_info',
    'protein_comprehensive_function_info',
    'protein_function_domain_relation',
    'protein_structure_function_relation',
    'protein_location_sequence_relation'
]

for table in tables:
    print(f"\n{'-'*20} 表 {table} 结构 {'-'*20}")
    cursor.execute(f"DESCRIBE {table}")
    columns = cursor.fetchall()
    for column in columns:
        print(column)

cursor.close()
conn.close() 