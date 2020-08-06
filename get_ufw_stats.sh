#!/bin/bash
awk 'match($0, /SRC=[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/){print substr($0, RSTART+4, RLENGTH-4)}' /var/log/ufw.log | sort | uniq -c | sort -n
