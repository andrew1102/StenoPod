#!/bin/bash

title=$1
title_dir=$REPO/.cache/$title
mkdir -p $title_dir
ffmpeg -i $REPO/audio/$title.mp3 -ac 1 -ar 16000 -f segment -segment_time 10 -c copy $title_dir/"$title"_%03d.flac

for file in $title_dir/*.flac; do
        line = $(basename file)
        echo $line
        python "$REPO"/scripts/transcriber.py "${file%.*}".flac
done
