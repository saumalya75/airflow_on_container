
  
# AirflowOnContainer

### A containerised application hosting Airflow, using CeleryExecutor with Redis and Postgres.

## 1. Introduction:
__What is Airflow?__
[Airflow](https://airflow.apache.org/docs/stable/) is a data pipeline workflow scheduler tool. User can schedule numerous kinds of tasks and define inter dependency using Airflow. Airflow workflows and tasks are written in python. It comes under _**configuration as code**_ paradigm.  But I bet you already knew that, given that you are here. So let's talk about the project then!

This application gives you an end to end setup of airflow (ready to launch) using celery executor, Redis message broker service and Postgres metadata store. All these tools are set up using docker containers.

## 2. Pre-requisite:
Not much, just a few things:

1. Install (if not installed already) latest version of [Docker and Docker-compose](https://docs.docker.com).

2. Install (if not installed already) latest version of [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

## 3. Getting the application/code:
**Easy-peasy!**

The entire project is available on my BitBucket repository  **`https://bitbucket.org/saumalya75/airflowoncontainer/src/master/`**, which can be cloned using **`git clone git@bitbucket.org:saumalya75/airflowoncontainer.git`**.

## 4. Usage:
#### This project focuses on launching a fully setup containerised Airflow environment. Provided codebase launches an Airflow server using Postgres database, CeleryExecutor with Redis.
_Anyone can clone the code base and do there own modification on it to suit there personal need._

#### Following steps need to be followed to launch a brand new Airflow server:
1. Login to the machine where you want to launch the Airflow containers.
2. Install required softwares, follow pre-requisite section.
3. Clone master branch (always contains the latest stable version) from the previously mentioned repo.
4. Create an empty directory named _`pgdata/`_ in the application root folder (cloned folder).
5. Create `.env` file by copying `.env-template` file and provide your set of intended configuration. Our application will use these values.
6. Create `script/create-user.py` file by copying `script/create-user-template.py` file and provide intended airflow credentials. These credentials will be required to log into Airflow WebUI.
7. Execute _`docker-compose up`_ command in the terminal file to run the application.
8. Open `http://0.0.0.0:8080` on your browser, login using the configured credentials from point 6.

#### N.B.: Please note, base image for airflow web server, scheduler, flower and worker is available at docker hub: _`saumalya75/airflowoncontainer:1.0.0`_.

### Adding new Dag:
1. Create your own dag files,
2. Put those in the `airflow_home/dag` folder,
3. Run the application,
4. If the application is already running, Wait for 30 seconds, new dags will be available in WebUI. **Voila!!**

## 5. Conclusion:

Let me end the article with thanking you for going through the article. It will be highly appreciated if anyone have any suggestions, ideas to implement. In case of any queries, suggestion, I am available on _+91-9593090126_ and saumalya75@gmail.com.