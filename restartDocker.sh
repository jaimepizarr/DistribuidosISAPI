#!/bin/bash

nginx="nginx"
postgres="postgres"
web="distribuidosisapi_web"

function exists_in_list() {
    LIST=$1
    DELIMITER=$2
    VALUE=$3
    LIST_WHITESPACES=`echo $LIST | tr "$DELIMITER" " "`
    for x in $LIST_WHITESPACES; do
        if [ "$x" = "$VALUE" ]; then
            return 1
        fi
    done
    return 0
}
while :
do

    containerNginx=$(docker ps -a -f ancestor=$nginx --format "{{.Names}}" )
    containerDB=$(docker ps -a -f ancestor=$postgres --format "{{.Names}}" )
    containerWeb=$(docker ps -a -f ancestor=$web --format "{{.Names}}" )
    containersAll="${containerNginx} ${containerDB} ${containerWeb}"

    containerNginx=$(docker ps -f ancestor=$nginx --format "{{.Names}}" )
    containerDB=$(docker ps -f ancestor=$postgres --format "{{.Names}}" )
    containerWeb=$(docker ps -f ancestor=$web --format "{{.Names}}" )
    containersAct="${containerNginx} ${containerDB} ${containerWeb}"

    DELIMITER=" "

    for cont in $containersAll; do
        if exists_in_list "$containersAct" "$DELIMITER" "$cont"; then
            docker start $cont
        fi
    done
    sleep 5
done