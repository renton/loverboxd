#!/bin/bash

while true; do
    flask deploy
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done

if [ "$FLASK_ENV" == "development" ]; then
    echo "*** Running in development mode ***"
    flask run
elif [ "$FLASK_ENV" == "production" ]; then
    echo "*** Running in production mode ***"
    exec gunicorn loverboxd:app \
        -b :${FLASK_APP_PORT} \
        --access-logfile - \
        --error-logfile - \
        --timeout 240 \
        --workers 3 \
        --reload
fi
