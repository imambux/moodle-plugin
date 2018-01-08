#!/bin/bash
echo "Stopping service"
stat=1
COUNTER=0

swait()
{
    echo -ne "Waiting for service to stop"
    until [[ $stat -eq 0 ]]
    do
        stat=$(netstat -lnt | awk '$4 ~ /:5001$/' |wc -l)
        COUNTER=$((COUNTER+1))
        if [ $COUNTER == 8 ] ; then
            echo -e '\nError - Service stop failed'
            exit;
        fi
        echo -ne "."
        sleep 2
    done
}

service_stop()
{
    for pid in `ps augx | grep gunicorn | grep -v grep | awk '{print $2}'`;
    do
        echo "Killing PID" $pid
        kill $pid
    done
}

service_stop
swait

echo -e "\nService stopped successfully"
