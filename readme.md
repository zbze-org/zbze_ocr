# Install airflow with postgres, redis, pandas, ssh, celery

```sh
pip install "apache-airflow[celery,postgres,redis,pandas,ssh]==2.7.2" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.2/constraints-3.8.txt"
```

# setup postgres
```sh
psql -h localhost -p 5432
```

```sql
CREATE DATABASE airflow_db;
CREATE USER zbze_ocr WITH PASSWORD '12345';
GRANT ALL PRIVILEGES ON DATABASE airflow_db TO zbze_ocr;
GRANT ALL PRIVILEGES ON DATABASE airflow_db TO zbze_ocr;
GRANT ALL ON SCHEMA public TO zbze_ocr;
```

# airflow postgres connection
```
sql_alchemy_conn = postgresql+psycopg2://zbze_ocr:12345@localhost:5432/airflow_db
```

# celery executor
```
executor = CeleryExecutor
```

# run airflow
```sh
airflow webserver -p 8080
```

```shell
airflow scheduler
```

```sh
airflow celery worker
```