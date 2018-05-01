#!/bin/sh

while true; do
    sleep 10
    flask deploy
    if [[ "$?" == "0" ]]; then
        echo Deploy success
        break
    fi
    echo Deploy command failed, retrying in 10 secs...
done

flask buildindex

exec gunicorn -b :5000 --access-logfile - --error-logfile - manage:app
