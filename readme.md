# Install airflow with postgres, redis, pandas, ssh, celery

```sh
pip install "apache-airflow[celery,postgres,redis,pandas,ssh]==2.7.2" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.2/constraints-3.8.txt"
```

# setup postgres
```sh
psql -h localhost -p 5432
```

## install postgresql and create db and user
```sql
CREATE DATABASE zbze_ocr_db;
CREATE USER zbze_ocr WITH PASSWORD '12345';
GRANT ALL PRIVILEGES ON DATABASE zbze_ocr_db TO zbze_ocr;
GRANT ALL PRIVILEGES ON DATABASE zbze_ocr_db TO zbze_ocr;
GRANT ALL ON SCHEMA public TO zbze_ocr;
```

# Config 

```sh
echo $(pwd)"/dags"
```

add path to [airflow.cfg](airflow.cfg) dags_folder=<dir>/dags
```text
dags_folder = /home/panagoa/PycharmProjects/zbze_ocr/dags
```

add path to [airflow.cfg](airflow.cfg) dag_processor_manager_log_location=<dir>/logs/dag_processor_manager/dag_processor_manager.log
```text
dag_processor_manager_log_location = /home/panagoa/PycharmProjects/zbze_ocr/logs/dag_processor_manager/dag_processor_manager.log
```

## airflow postgres connection
```
sql_alchemy_conn = postgresql+psycopg2://zbze_ocr:12345@localhost:5432/zbze_ocr_db
```

## celery executor
```
executor = CeleryExecutor
```

```shell
export AIRFLOW_HOME=$(echo $(pwd))
```

# run airflow
```sh
AIRFLOW_HOME=$(echo $(pwd)) airflow webserver -p 8080
```

```shell
AIRFLOW_HOME=$(echo $(pwd)) airflow scheduler
```

```sh
AIRFLOW_HOME=$(echo $(pwd)) airflow celery worker
```

```shell
AIRFLOW_HOME=$(echo $(pwd)) airflow users create \
          --username zbze \
          --firstname zbze \
          --lastname ocr \
          --role Admin \
          --email admin@example.org
```

```shell
AIRFLOW_HOME=$(echo $(pwd)) airflow db check
```

```shell
AIRFLOW_HOME=$(echo $(pwd)) airflow db migrate
```

```shell
AIRFLOW_HOME=$(echo $(pwd)) airflow db check-migrations
```

## stop all airflow process 
```sh
ps -ef | grep 'airflow' | grep -v grep | awk '{print $2}' | xargs -r kill -9
```