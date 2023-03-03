#!/bin/bash

for f in ./*.orb; do
    # do some stuff here with "$f"
    # remember to quote it or spaces may misbehave
    wine ~/.wine/drive_c/SOAP/bin64/soap.exe "$f"
done
