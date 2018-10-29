#!/bin/bash
 
find $HOME/.rmv/* -mtime +t -exec rm -f {} \;
