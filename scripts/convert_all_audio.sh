#!/bin/bash

#Change mp3 to whatever audio type you're using
for file in $REPO/audio/*.mp3; do
#    new_file="$REPO"/"audio"/"${file%.*}".flac
    new_file="${file%.*}".flac
    ffmpeg -i "$file" -y -ac 1 -ar 16000 "$new_file"
done
