#!/bin/bash

title=$1
ffmpeg -i $REPO/audio/$title.mp3 -ac 1 -ar 16000 -f segment -segment_time 10 -c copy $REPO/.cache/"$title"%03d.mp3

for file in $REPO/.cache/*$title*.mp3; do
	x="${file//.mp3/.flac}" 
	ffmpeg -i $file -ac 1 -ar 16000 $x
	python $REPO/scripts/short_transcriber.py $(basename $x)
	rm $file
	rm $x
done
