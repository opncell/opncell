#!/bin/bash 

checkMongo() {

    command="ps aux | grep mongod | awk '\$8 == \"I+\" || \$8 == \"Is\" || \$8 == \"T\" {print \$8}'"
    status=$(eval "$command")
    if test "$status" != "T"; then
       pid_command="ps aux | grep mongod | awk '\$8 == \"I\" || \$8 == \"I+\" || \$8 == \"Is\" || \$8 == \"S\" {print \$2}'"
       pid=$(eval "$pid_command")
       kill -9 "$pid"
    fi
}

checkMongo
