
  

# AirflowOnContainer

  

### A containerised application hosting Airflow, using CeleryExecutor with Redis and Postgres.

## 1. Introduction:

Airflow is a data pipeline workflow scheduler tool. User can schedule numerous operations and define inter dependency using Airflow. Airflow workflows and tasks are written in python. So it comes under _**configuration as code**_ paradigm. But I bet you already knew that, given that you are here. So let's talk about the project then!

  

__This application focuses on two distinct processes:__

1. Get the Airflowing, i.e. set up Airflow to run on containers(_section 3_),

2. Develop a demo pipeline(_section 4_) which implements important and frequently used airflow concepts like:

* Create custom plugins (custom sensor, operator, hooks etc),

* Use custom plugins in Dag,

* Use XCom to setup communication between tasks,

* Create dynamic dag based on configuration file etc.

I have skipped the very basic examples as those are readily available in Airflow official website.

## 2. Pre-requisite:

### 2.1. Environment:

Not much, just a few things:

1. Install (if not installed already) latest version of [Docker and Docker-compose](https://docs.docker.com) installed in your system.

2. Install (if not installed already) latest version of [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

### 2.2. Getting the application/code:

The entire project is available on my BitBucket repository **`https://bitbucket.org/saumalya75/airflowoncontainer/src/master/`** can be cloned using **`git clone git@bitbucket.org:saumalya75/airflowoncontainer.git`**.

## 3. Setup Airflow:

#### This section focuses on launching an fully setup containerised Airflow environment. Provided codebase launches an Airflow server using Postgres database, CeleryExecutor with Redis.

_Anyone can clone the code base and do there own modification on it to suit there personal need._

### 3.1. Setup Steps:

#### Following steps need to be followed to launch an Airflow server:

1. Install required softwares, follow pre-requisite section.

2. Clone `saumalya75/airflowoncontainer`  [repository](https://bitbucket.org/saumalya75/airflowoncontainer/src/master/).

3. Create an empty directory named _`pgdata/`_ in the application root folder (cloned folder).

4. Create `.env` file by copying `.env-template` file and provide your set of intended configuration. Our application will use these values.

5. Open `http://0.0.0.0:8080` on your browser.

#### N.B.: Please note, base image for airflow web server, scheduler, flower and worker is available at docker hub: _`saumalya75/airflowoncontainer:latest`_.

### 3.2. Behind the back:

Let's discuss exactly what is going on behind the back:

#### 3.2.1. Docker Images:

In this application, total four images are used:

*  `minio/minio` (Existing official image from docker hub library)

*  `redis:5.0.5` (Existing official image from docker hub library)

*  `postgres:9.6` (Existing official image from docker hub library)

*  `saumalya75/airflowoncontainer:latest` (Built from available Dockerfile or pulled from `saumalya75/airflowoncontainer` repository)

#### 3.2.2. Docker-Compose:

Two docker-compose files are provided, using those either Celery or Local executor type Airflow server can be lasuched:

*  `docker-compose-CeleryExecutor.yml`

*  `docker-compose-LocalExecutor.yml`

##### 3.2.3. Container Properties:

Several container properties are provided in docker compose files:

###### Postgres Volume:

...

volumes:

- ./pgdata:/var/lib/postgresql/data/pgdata

...

###### Airflow services volume:

...

volumes:

- ./airflow_home:/usr/local/airflow

- ./app_home:/usr/local/app

...

###### Each services will expose relevant ports:

...

ports:

- "8080:8080"

...

###### Whereas all the services will receive relevant environment variables using environment tags:

...

environment:

- LOAD_EX=${V_LOAD_EX}

- FERNET_KEY=${V_FERNET_KEY}

- EXECUTOR=Celery

- REDIS_HOST=redis

- REDIS_PORT=${V_REDIS_PORT}

- REDIS_PASSWORD=${V_REDIS_PASSWORD}

...

Other than these some more properties are provided, please check the docker-compose files for other details.

#### 3.2.4. Boot Up:

To spin up the server, execute:

`docker-compose -f <compose file name with absolute path> up`

## 4. Develop Pipeline:

### 4.1. Dynamic Dag:

As already mentioned we will touch a few frequently used important concepts of Airflow, let's start with creating a dag that uses config file to create dynamic dag structure during run time. We will not cover creating simple tags, as there are already lot of examples available on internet. Following are the file structure:

```

.

+-- airflow_home

| +-- dags

| | +-- configurable_data_pipeline_demo.py

| | +-- dag_configuration_demo.json

```

`dag_configuration_demo.json` file contains the configuration for the files to run, based on the content provided tasks are added to the dag - `configurable_data_pipeline_demo` in runtime via `configurable_data_pipeline_demo.py` file.

  

For each source file three tasks will be executed:

* Trigger file sensor on Minio server

* Source file sensor on AWS s3 server

* File processor

  

#### 4.2. Custom Hook:

To support for minio, some methods of airflow provided `s3Hook` has been overridden by creating `CustomS3MinioHook` class, the code is present in:

```

.

+-- airflow-home

| +-- plugins

| | +-- hooks

| | | +-- custom_s3_minio_hook.py

```

Notice, `CustomS3MinioHook` class is serving as an interface, and we are actually implementing our logic in `CustomS3Hook` and `CustomMinioHook` classes. We are using exceptional capabilities of object __creation__ magic method: `__new__` and object __initialization__ magic method: `__init__`.

_Similarly any logic can be implemented in a Sensor class, and can be used as Airflow sensor._

  

#### 4.3. Custom Sensor:

Custom sensor is implemented based on these overridden methods in custom hook and already available functionalities of airflow provided s3hook.

Our custom s3/minio sensor is implemented by inheriting from `BaseSensor` class. We used `@apply_defaults` decorator on the sensor constructor (`__init__` method), and one `poke` method is written, handling the logic of file sensing. Please keep in mind the actual communication to s3/minio server is done by methods available in hooks. Although implementing communication logic in sensor class is not forbidden, at the end of the day, it is just another python file. But that is frowned upon and not a very good design. our custom sensor code file is as follows:

```

.

+-- airflow-home

| +-- plugins

| | +-- sensors

| | | +-- custom_s3_sensor.py

```

#### 4.4. Custom operator:

Using the same methodology, I have implemented one custom operator, which inherits from `BaseOperator`. The operator does not do much, it just reads the file and takes count and puts that on `Xcom`. As my soul focus of this article is to set up and familiarise with airflow concept, I did not focused on file processing logic, maybe some other day. Custom Oerator is available at:

```

.

+-- airflow-home

| +-- plugins

| | +-- operators

| | | +-- custom_file_load_operator.py

```

#### 4.5. Custom Plugins:

Although we created separate `.py` file for our custom sensor and operators, airflow will not consider those unless we explicitly point it out. To do so, I created one plugin file and declared our custom elements in it. The declaration has a specific structure. The concept is to create one plugin class `CustomPlugin` inheriting `AirflowPlugins`, and declare class variables - `sensors`, `operators` as python list and include all the elements in it. All other type of Airflow elements can be customised and injected in Airflow in similar way. The code is present at:

```

.

+-- airflow-home

| +-- plugins

| | +-- custom_plugin.py

```

#### Xcom data:

All three tasks - `minio_sensor`,`s3_sensor` and `data_processor` is communicating (source file details) between them via `Xcom` variables. From one task values are pushed into `Xcom`, and other tasks are reading the values using same keys. Please checkout `_trigger_file_to_xcom` method present in `custom_s3_sensor.py` file to understand how to push a variable to Xcom and `_extract_xcom_data` will help you understand how to pull data from Xcom. Basically, the `task_instance`, present in `context`,

object has `xcom_pull` and `xcom_push` methods, which are used to implement Xcom communication. Please go through the files for detailed example.

  

#### Execute the dag:

Once the airflow server is up and running, all dag files present in `airflowoncontainer/airflow_home/dags` will be available in the WebUI. Now for our demo's sake, we will try to execute `configurable_data_pipeline_demo` dag. Once the dag file is triggered, all minio_sensor tasks will wait for trigger files to be present in minio bucket. Please login to minio (credentials as provided in .env file while setting up) in '_http://0.0.0.0:9000_'. Create a bucket there named '__airflow__' and one folder named '__trigger__' folder in the bucket. Then upload files from `airflowoncontainer/app_home/data` to the minio folder, please change the datepart in the name of the files to current date. You can upload some files at a go and check whether the tasks are succeeding or not. Once `minio_trigger` tasks are passed, the `s3_trigger` tasks will be pending. I will let you figure out this path.

__Hint:__ The file details are present in the content of corresponding trigger files are expected to be present in `AWS S3`.

  

## 5. Credit, where it's due

The Airflow setup is derived from the excellent [repository](https://github.com/puckel/docker-airflow) created by puckel_. I have only counterfitted the set up based on our demo requirement. About the dag, sensor, operator, plugin files, I took help from numerous articles present on internet. Although most of the codes are written by me, but I had to learn from somewhere, right!

  

## 6. Conclusion

Let me end the article with thanking you for going through the article. It will be highly appreciated if anyone have any suggestions, ideas to implement. In case of any queries, suggestion, I am available on _+91-9593090126_ and saumalya75@gmail.com.



