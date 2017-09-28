#! /system/bin/sh
fullname=$1
name=${fullname%.*}
python3 macro2m.py $fullname $name.m
echo "copy $name.m to /sdcard/GameTuner"
cp $name.m /sdcard/GameTuner

