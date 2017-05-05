#!/bin/bash

curl -c /tmp/cookies "https://drive.google.com/uc?export=download&id=0B1Xio1gViu12ZTNGdk1jRHliOVE" \
    > /tmp/intermezzo.html
curl -L -b /tmp/cookies \
    "https://drive.google.com$(cat /tmp/intermezzo.html\
    | grep -Po 'uc-download-link" [^>]* href="\K[^"]*' \
    | sed 's/\&amp;/\&/g')" > "model.bin.gz"
