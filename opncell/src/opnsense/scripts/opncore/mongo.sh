#!/bin/bash

checkMongo() {
    
    command="ps aux | grep mongod | awk '\$8 == \"I+\" || \$8 == \"Is\" || \$8 == \"T\" {print \$8}'"
    status=$(eval "$command")    
    echo $status
    if test "$status" == "T"   ; then
       pid_command="ps aux | grep mongod | awk '\$8 == \"T\" {print \$2}'"
       pid=$(eval "$pid_command")
      kill -9 $pid
      echo $pid
      mongo_binary_path=$(which mongod)
      directory_path=$(dirname "$mongo_binary_path")
     # echo $directory_path
      cd $directory_path || exit 1
     mkdir -p ./data/db
     #chmod +x ./data/db
     mongod --dbpath ./data/db &
  sleep 2      
    fi

   if test -z  "$status" ; then
      mongo_binary_path=$(which mongod)
      directory_path=$(dirname "$mongo_binary_path")
     # echo $directory_path
      cd $directory_path || exit 1
     mkdir -p ./data/db
     #chmod +x ./data/db
     mongod --dbpath ./data/db &
sleep 2
 fi
}

checkMongo
