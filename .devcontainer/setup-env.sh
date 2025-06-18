#!/bin/bash

echo " Sjekker om .env eksisterer..."

if [ ! -f .env ] && [ -f .env.template ]; then
    cp .env.template .env
    echo ".env opprettet fra .env.template"
else
    echo ".env finnes allerede, eller .env.template mangler"
fi


