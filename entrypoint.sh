#! /usr/bin/env bash

echo $INPUT_APP_PEM | base64 -d > pem.txt
#echo $INPUT_APP_PEM > pem.txt
python token_getter.py
