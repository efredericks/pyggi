#!/bin/bash

grep "Difference" $1 | cut -d ' ' -f 4 | sort
