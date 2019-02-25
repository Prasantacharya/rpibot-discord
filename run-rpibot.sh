#!/bin/bash

while true; do
    git pull;
    python rpibot.py || exit 1;
done
