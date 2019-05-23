#!/bin/bash
for i in {0..9}
do
    ./playpl.sh "lookt.mac -d 2" 5437$i
    sleep 2
done