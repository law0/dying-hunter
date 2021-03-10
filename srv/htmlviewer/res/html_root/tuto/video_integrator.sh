#!/bin/bash
shDir=$( dirname "${BASH_SOURCE[0]}" )

if [[ "$1" == "" ]]
then
    echo "Please add the path of the video to be integrated as argument"
fi

VI_SOURCE=$1
VI_SOURCE_NAME=$(basename "$VI_SOURCE" | cut -d. -f1)

ffmpeg -i ${VI_SOURCE} -i ${shDir}/back_music.mp3 -map 0:v -map 1:a -c:v libvpx-vp9 -crf 30 -b:v 0 -b:a 128k -c:a libopus -shortest ${shDir}/${VI_SOURCE_NAME}.webm
