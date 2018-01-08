#!/bin/bash
stat=0
COUNTER=0

#gunicorn -w 2 main:app -b 0.0.0.0:5001 -D --log-level=info

swait()
{
    echo -ne "Waiting for service to start"
    until [[ $stat -ge 1 ]]
    do
        stat=$(netstat -lnt | awk '$4 ~ /:5001$/' | wc -l)
        COUNTER=$((COUNTER+1))
        if [ $COUNTER == 5 ] ; then
            echo -e '\nError - Service start failed.'
            exit;
        fi
        echo -ne "."
        sleep 2
    done
}

service_start()
{
    echo "Starting service"
    gunicorn -b 0.0.0.0:5001 main:app 
}


service_start
swait

echo -e "\nService started successfully."
