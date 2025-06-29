#!/bin/sh
if [ ! -f .env ] && [ -f .env.template ];then
    cp .env.template .env
    echo ".env created from .env.template"
else
    if [ -f .env ];then
        echo ".env already exists, skipping creation."
    else
        echo ".env.template not found, please create a .env file manually."
    fi
fi
