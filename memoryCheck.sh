#!/bin/bash

vmstat > vmstat.txt
top -b -n 2 > top.txt
free > free.txt