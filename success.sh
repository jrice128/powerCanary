#!/usr/bin/env bash
echo none >/sys/class/leds/led0/trigger
echo "MESSAGE"
echo 0 >/sys/class/leds/led0/brightness
for i in 1 2 3 4 5 6 7 8 9 10
do
    echo 1 >/sys/class/leds/led0/brightness
    sleep 0.1
    echo 0 >/sys/class/leds/led0/brightness
    sleep 0.1
echo 1 >/sys/class/leds/led0/brightness
sleep 1
done
echo "END MESSAGE"
echo mmc0 >/sys/class/leds/led0/trigger