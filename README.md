
### `ESP32_movement.ino`

This sketch uses an ESP32 with a PIR motion sensor and an ultrasonic distance sensor to detect presence and respond with spoken output via `espeak-ng` (German voice) through PWM audio on GPIO18. The speaker is driven via a BC337 NPN transistor, with a 100 nF capacitor between base and emitter for signal smoothing. The ultrasonic sensor’s ECHO pin (5 V) is stepped down to a safe 3.3 V using a voltage divider (1 kΩ + 2 kΩ) before connecting to GPIO17. A momentary push button on GPIO19 lets you query whether motion was recently detected and what the current distance is. The ESP32 samples every 200 ms and only speaks “Hallo! Herzlich Willkommen!” if motion or a >10% distance change occurred within the last second — limited to once every 15 seconds.

Power is supplied by **4× AA NiMH batteries**, wired in series (~5.2–5.6 V). Both sensors (PIR and ultrasonic) are connected directly to this battery voltage at their **VIN/VCC pins**. The ESP32 is powered via its **VIN** and **GND** pins.

The sketch requires the following libraries by [@pschatzmann](https://github.com/pschatzmann):

- [`arduino-audio-tools`](https://github.com/pschatzmann/arduino-audio-tools)  
  → for audio streaming and PWM output  
- [`arduino-posix-fs`](https://github.com/pschatzmann/arduino-posix-fs)  
  → for in-memory access to `espeak-ng` voice data  
- [`arduino-espeak-ng`](https://github.com/pschatzmann/arduino-espeak-ng)  
  → compact, multilingual TTS engine with German support

### `ev3_alarm_clock.py`

Alarm clock script for LEGO EV3 showing large time display with smaller alarm status below. Set or change alarm using left/right buttons, toggle with center, exit with back. Rings 10 times on alarm. Touch sensor on input 1 lights EV3 LED when pressed. Time shown in Berlin timezone (UTC+2 if `pytz` unavailable). Install font with `sudo apt-get install fonts-dejavu-core`. Consider enabling NTP sync on Wi-Fi by leveraging `sntp`, e.g. adding an executable script `/etc/network/if-up.d/ntp-sync` with 
```
#!/bin/sh
# ntp-sync: called automatically when wlan0 comes online

IFACE="$1"

if [ "$IFACE" = "wlan0" ]; then
    echo "$(date): wlan0 is up — syncing time" >> /var/log/ntp-sync.log
    /usr/bin/sntp pool.ntp.org >> /var/log/ntp-sync.log 2>&1
fi```
