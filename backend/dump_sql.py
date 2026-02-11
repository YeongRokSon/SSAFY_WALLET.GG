import sqlite3
import os

# 파일 이름이 맞는지 확인해 (파란색 아이콘 파일 이름)
db_file = 'db.sqlite3'

if not os.path.exists(db_file):
    print("에러: db.sqlite3 파일을 찾을 수 없어! 폴더 위치를 확인해줘.")
else:
    conn = sqlite3.connect(db_file)
    # 전체 DB 구조를 schema.sql 파일로 저장함
    with open('schema.sql', 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            # 테이블 생성(CREATE) 문구만 골라서 저장함
            if 'CREATE TABLE' in line:
                f.write(line + '\n')
    conn.close()
    print("성공! schema.sql 파일이 생성되었어.")