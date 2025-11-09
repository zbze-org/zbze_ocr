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
CREATE USER zbze_ocr WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE zbze_ocr_db TO zbze_ocr;
GRANT ALL ON SCHEMA public TO zbze_ocr;
```

**Note:** Replace `your_secure_password_here` with a strong password and update it in your `.env` file.

# Config 

## create airflow.cfg from airflow.cfg.template

```sh
echo $(pwd)"/dags"
```

add path to [airflow.cfg](airflow.cfg) dags_folder=<dir>/dags
```text
dags_folder = /path/to/your/zbze_ocr/dags
```

**Example:** `dags_folder = /home/username/PycharmProjects/zbze_ocr/dags`

add path to [airflow.cfg](airflow.cfg) dag_processor_manager_log_location=<dir>/logs/dag_processor_manager/dag_processor_manager.log
```text
dag_processor_manager_log_location = /path/to/your/zbze_ocr/logs/dag_processor_manager/dag_processor_manager.log
```

**Example:** `dag_processor_manager_log_location = /home/username/PycharmProjects/zbze_ocr/logs/dag_processor_manager/dag_processor_manager.log`

## airflow postgres connection
```
sql_alchemy_conn = postgresql+psycopg2://zbze_ocr:your_password@localhost:5432/zbze_ocr_db
```

**Note:** Replace `your_password` with the password you set when creating the PostgreSQL user.

## celery executor
```
executor = CeleryExecutor
```

```shell
export AIRFLOW_HOME=$(echo $(pwd))
```

```shell
AIRFLOW_HOME=$(echo $(pwd)) airflow db init
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

## stop all airflow process 
```sh
ps -ef | grep 'airflow' | grep -v grep | awk '{print $2}' | xargs -r kill -9
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

cp tesseract trained model to tessdata
```shell
sudo cp data/tesstrain/kbd/trained_data/kbd.traineddata  /usr/share/tesseract-ocr/5/tessdata/
```