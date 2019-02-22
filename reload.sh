#!/bin/bash

git pull
docker stop rpibot
docker rm rpibot
docker build -t rpibot .
docker run -d --name rpibot rpibot
