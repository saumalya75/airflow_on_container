
  
# AirflowOnContainer

### A containerised application hosting Airflow, using CeleryExecutor with Redis and Postgres.
## 1. Introduction:
__What is Airflow?__
Airflow is a data pipeline workflow scheduler tool. User can schedule numerous kinds of stuff and define inter dependency using Airflow. Airflow workflows and tasks are written in python. So it comes under _**configuration as code**_ paradigm.  But I bet you already knew that, given that you are here. So let's talk about the project then!
__This application focuses on two distinct processes:__
1. Get the Airflowing, i.e. set up Airflow to run on containers(_section 3_),
2. Develop a demo pipeline(_section 4_) which implements important and frequently used airflow concepts like:
	* Create custom plugins (custom sensor, operator, hooks etc),
	* Use custom plugins in Dag,
	* Use XCom to setup communication between tasks,
	* Create dynamic dag based on configuration file etc.
I have skipped the very basic examples as those are readily available in Airflow official website.
## 2. Pre-requisite:
Not much, just a few things:
1. Install (if not installed already) latest version of [Docker and Docker-compose](https://docs.docker.com) installed in your system.
2. Install (if not installed already) latest version of [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
## Getting the application/code:
**Easy-peasy!**
The entire project is available on my BitBucket repository  **`https://bitbucket.org/saumalya75/airflowoncontainer/src/master/`** can be cloned using **`git clone git@bitbucket.org:saumalya75/airflowoncontainer.git`**.
## 3. Setup Airflow:
#### This section focuses on launching an fully setup containerised Airflow environment. Provided codebase launches an Airflow server using Postgres database, CeleryExecutor with Redis.
_Anyone can clone the code base and do there own modification on it to suit there personal need._
### 3.1. Setup Steps:
#### Following steps need to be followed to launch an Airflow server:
1. Install required softwares, follow pre-requisite section.
2. Clone `saumalya75/airflowoncontainer` [repository](https://bitbucket.org/saumalya75/airflowoncontainer/src/master/).
3. Create an empty directory named _`pgdata/`_ in the application root folder (cloned folder).
4. Create `.env` file by copying `.env-template` file and provide your set of intended configuration. Our application will use these values.
~~5. Create `script/create-user.py` file by copying `script/create-user-template.py` file and provide intended airflow credentials. These credentials will be required to log into Airflow WebUI.~~
~~6. Follow _`exec_command.txt`_ file to run the application.~~
7. Open `http://0.0.0.0:8080` on your browser~~, login using the configured credentials from point 5~~.
#### N.B.: Please note, base image for airflow web server, scheduler, flower and worker is available at docker hub: _`saumalya75/airflowoncontainer:2.0.0`_.
### 3.2. Behind the back:
Let's discuss exactly what is going on behind the back:
##### 3.2.1. Docker Images:
In this application, total four images are used:
* `minio/minio` (Existing official image from docker hub library)
* `redis:5.0.5`  (Existing official image from docker hub library)
* `postgres:9.6`  (Existing official image from docker hub library)
* `saumalya75/airflowoncontainer:2.0.0` (Built from available Dockerfile or pulled from `saumalya75/airflowoncontainer` repository)
##### 3.2.2. Docker-Compose:
Two docker-compose files are provided, using those either Celery or Local executor type Airflow server can be lasuched:
* `docker-compose-CeleryExecutor.yml`
* `docker-compose-LocalExecutor.yml` 
##### 3.2.3. Container Properties:
Several container properties are provided in docker compose files:
###### Postgres Volume:
    volumes:
    - ./pgdata:/var/lib/postgresql/data/pgdata
###### Airflow services volume:
    volumes:
    - ./airflow_home:/usr/local/airflow
    - ./app_home:/usr/local/app
###### Each services will expose relevant ports:
    ports:
    - "8080:8080"
###### Whereas all the services will receive relevant environment variables using environment tags:
    environment:
    - LOAD_EX=${V_LOAD_EX}
    - FERNET_KEY=${V_FERNET_KEY}
    - EXECUTOR=Celery
    - REDIS_HOST=redis
    - REDIS_PORT=${V_REDIS_PORT}
    - REDIS_PASSWORD=${V_REDIS_PASSWORD}
Other than these some more properties are provided, please check the docker-compose files for other details.
##### 3.2.4. 
To spin up the server, execute:
`docker-compose -f <compose file name with absolute path> up`
## 4. Develop Pipeline:
In this application we are developing an demo pipeline for a set of source files. For each source file three tasks will be executed:
* Trigger file sensor on Minio server
* Source file sensor on AWS s3 server
* File processor

_Processing for each file will start when the trigger file is provided on specific bucket and path. The trigger file will also hold AWS S3 bucket path and name of actual source file. That information will be passed to AWS S3 sensor via XCom, S3 file sensor will await for the arrival of actual source file(source file detail will be pulled from XCom) and once the file is available file processor will run. Now this file processor is not doing much, just taking count and push the count to XCom, but the setup will be same for any complex file processing also._
_Moreover, there is a configuration json file which holds the information of which are the source files and the details of corresponding trigger files. This configuration file will be used to create dynamic Dag_

### Adding new Dag:
1. Create your own dag files,
2. Put those in the `airflow_home/dags` folder,
3. Run the application,
4. If the application is already running, Wait for 30 seconds, new dags will be available in WebUI. **Voila!!**
### Adding Plugins:
1. To add new plugins add .py files in respective folders,
2. Custom Operators will go in plugins/operators, Custom Sensors will go in plugins/sensors etc

_**P.S.:** We will discuss custom plugin building in detail in Section 4_
## 5. Conclusion:
Let me end the article with thanking you for going through the article. It will be highly appreciated if anyone have any suggestions, ideas to implement. In case of any queries, suggestion, I am available on _+91-9593090126_ and saumalya75@gmail.com.