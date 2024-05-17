#!/bin/bash

echo -n "sudo password for [$USER]: "
read -s input

SUPW="$input"

(nohup ./checkBot/bin/python3 bot.py $SUPW &)
