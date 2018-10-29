#!/bin/bash

#Change mp3 to whatever audio type you're using
for file in $REPO/audio/*.mp3; do
	x=$(basename $file)
	x=${x%.*}.flac
	x=$REPO/.cache/$x
        ffmpeg -i $file -y -ac 1 -ar 16000 "$x"
done
