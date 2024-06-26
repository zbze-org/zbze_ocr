# setup postgres
```sh
psql -h localhost -p 5432
```

## install postgresql and create db and user
```sql
CREATE DATABASE zbze_ocr_web_db;
CREATE USER zbze_ocr_web WITH PASSWORD '12345';
GRANT ALL PRIVILEGES ON DATABASE zbze_ocr_web_db TO zbze_ocr_web;
GRANT ALL ON SCHEMA public TO zbze_ocr_web;
```