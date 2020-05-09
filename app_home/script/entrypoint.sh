#!/usr/bin/env bash

# User-provided configuration must always be respected.
#
# Also User must respect the need of an application, after applications also have some rights.
# So if you want to use the application, better provide proper configuration.

TRY_LOOP="20"

# Global defaults initialization
: "${AIRFLOW_HOME:="/usr/local/airflow"}"
: "${AIRFLOW__CORE__FERNET_KEY:=${FERNET_KEY:="rEALLY_rEALLY_bAD_eNCRYPTON_kEY"}}"
: "${AIRFLOW__CORE__EXECUTOR:=${EXECUTOR:-Sequential}Executor}"

# Load DAGs examples (default: Yes), we are not kids, Come Onnnn!
if [[ -z "$AIRFLOW__CORE__LOAD_EXAMPLES" && "${LOAD_EX:=n}" == n ]]; then
  AIRFLOW__CORE__LOAD_EXAMPLES=False
fi

# Share it with other kenels, sharing is caring!
export \
  AIRFLOW_HOME \
  AIRFLOW__CORE__EXECUTOR \
  AIRFLOW__CORE__FERNET_KEY \
  AIRFLOW__CORE__LOAD_EXAMPLES \


# You know, when you wanna build customised product, you gotta have your own set of tools.
if [ -e "/usr/local/airflow/requirements.txt" ]; then
  $(command -v pip) install --user -r /usr/local/airflow/requirements.txt
fi

# It just waits untill you are ready. I just love it, don't you!
wait_for_port() {
  local name="$1" host="$2" port="$3"
  local j=0
  while ! nc -z "$host" "$port" >/dev/null 2>&1 < /dev/null; do
    j=$((j+1))
    if [ $j -ge $TRY_LOOP ]; then
      echo >&2 "$(date) - $host:$port still not reachable, giving up"
      exit 1
    fi
    echo "$(date) - waiting for $name... $j/$TRY_LOOP"
    sleep 5
  done
}

# Every executor apart from SequentialExecutor is so needy, they need sql databases to run. So here we through in our very own Postgres. Only SequentialExecutor can handle it business on it's own.
if [ "$AIRFLOW__CORE__EXECUTOR" != "SequentialExecutor" ]; then
  : "${POSTGRES_EXTRAS:-""}"

  AIRFLOW__CORE__SQL_ALCHEMY_CONN="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}${POSTGRES_EXTRAS}"
  export AIRFLOW__CORE__SQL_ALCHEMY_CONN

  # CeleryExecutor is in it's own league when it comes to being needy, it even needs a resut backend, talk about being self-insufficient.
  if [ "$AIRFLOW__CORE__EXECUTOR" = "CeleryExecutor" ]; then
    AIRFLOW__CELERY__RESULT_BACKEND="db+postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}${POSTGRES_EXTRAS}"
    export AIRFLOW__CELERY__RESULT_BACKEND
  fi

  # Now we wait till the supporting crew is ready to serve.
  wait_for_port "Postgres" "$POSTGRES_HOST" "$POSTGRES_PORT"
fi

# And we are back to CeleryExecutor again, again it is asking for a messenger just to manage it's workers, Now it's geting on my nerves.
if [ "$AIRFLOW__CORE__EXECUTOR" = "CeleryExecutor" ]; then
  : "${REDIS_PROTO:="redis://"}"
  : "${REDIS_DBNUM:="1"}"

  # When Redis is secured by basic auth, it does not handle the username part of basic auth, only a token
  if [ -n "$REDIS_PASSWORD" ]; then
    REDIS_PREFIX=":${REDIS_PASSWORD}@"
  else
    REDIS_PREFIX=
  fi

  AIRFLOW__CELERY__BROKER_URL="${REDIS_PROTO}${REDIS_PREFIX}${REDIS_HOST}:${REDIS_PORT}/${REDIS_DBNUM}"
  export AIRFLOW__CELERY__BROKER_URL

  # Again wait for supporting crew.
  wait_for_port "Redis" "$REDIS_HOST" "$REDIS_PORT"
fi

case "$1" in
  webserver)
    airflow initdb
    if [ "$AIRFLOW__CORE__EXECUTOR" = "LocalExecutor" ] || [ "$AIRFLOW__CORE__EXECUTOR" = "SequentialExecutor" ]; then
      # "Local" and "Sequential" executors will run everything in one container. The Family Guys, huh!!
      airflow scheduler &
    fi
    exec airflow webserver
    ;;
  worker|scheduler)
    # Give the databse a little break dude, let it get ready, then you can as many times as you want.
    sleep 10
    exec airflow "$@"
    ;;
  flower)
    sleep 10
    exec airflow "$@"
    ;;
  version)
    exec airflow "$@"
    ;;
  *)
    # The command is something like bash, not an airflow subcommand. Just run it in the right environment. Not that important basically.
    exec "$@"
    ;;
esac
