#!/usr/bin/env bash
sudo chown pi: /sys/class/leds/led0/trigger
sudo chmod u+w /sys/class/leds/led0/trigger

sudo chown pi: /sys/class/leds/led0/brightness
sudo chmod u+w /sys/class/leds/led0/brightness