#!/usr/bin/env python3
from ev3dev2.display import Display
from ev3dev2.button import Button
from ev3dev2.sound import Sound
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds
import time
from datetime import datetime, timedelta
from PIL import ImageFont

# Optional timezone support
try:
    from pytz import timezone
    berlin = timezone('Europe/Berlin')
    USE_PYTZ = True
except ImportError:
    USE_PYTZ = False

# Init hardware
btn = Button()
sound = Sound()
screen = Display()
sensor = TouchSensor('in1')  
leds = Leds()

# Fonts
font_big = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)

# Alarm state
alarm_set = False
alarm_hour = 7
alarm_minute = 0

def get_local_time():
    if USE_PYTZ:
        return datetime.now(berlin)
    else:
        return datetime.utcnow() + timedelta(hours=2)

def draw_main_screen(now, alarm_on, ah, am):
    screen.clear()
    time_str = now.strftime("%H:%M")
    alarm_str = "Alarm aus" if not alarm_on else "Alarm: {:02}:{:02}".format(ah, am)

    w, _ = screen.image.size
    time_w, _ = screen.draw.textsize(time_str, font=font_big)
    alarm_w, _ = screen.draw.textsize(alarm_str, font=font_small)

    screen.text_pixels(time_str, x=(w - time_w) // 2, y=10, font=font_big, clear_screen=False)
    screen.text_pixels(alarm_str, x=(w - alarm_w) // 2, y=60, font=font_small, clear_screen=False)
    screen.update()

def draw_centered_text(y, text, font):
    screen.clear()
    w, _ = screen.image.size
    text_w, _ = screen.draw.textsize(text, font=font)
    x = (w - text_w) // 2
    screen.text_pixels(text, x=x, y=y, font=font)
    screen.update()

def set_alarm_time(current_hour, current_minute):
    hour = current_hour
    minute = current_minute
    selected = "hour"

    while True:
        screen.clear()
        screen.text_pixels("Wecker stellen", x=10, y=5, font=font_small)
        h_str = "[{:02}]".format(hour) if selected == "hour" else "{:02}".format(hour)
        m_str = "[{:02}]".format(minute) if selected == "minute" else "{:02}".format(minute)
        setting = "{} : {}".format(h_str, m_str)
        setting_w, _ = screen.draw.textsize(setting, font=font_big)
        screen.text_pixels(setting, x=(screen.xres - setting_w) // 2, y=30, font=font_big)
        screen.update()

        if btn.left:
            selected = "hour"
            time.sleep(0.2)
        elif btn.right:
            selected = "minute"
            time.sleep(0.2)
        elif btn.up:
            if selected == "hour":
                hour = (hour + 1) % 24
            else:
                minute = (minute + 1) % 60
            time.sleep(0.2)
        elif btn.down:
            if selected == "hour":
                hour = (hour - 1) % 24
            else:
                minute = (minute - 1) % 60
            time.sleep(0.2)
        elif btn.enter:
            return hour, minute
        elif btn.backspace:
            return current_hour, current_minute

def ring_alarm():
    sound.speak("Aufstehen!")
    for i in range(10):
        sound.beep()
        time.sleep(1)

def main():
    global alarm_set, alarm_hour, alarm_minute

    now = get_local_time()
    alarm_hour = now.hour
    alarm_minute = now.minute
    alarm_set = False

    while True:
        now = get_local_time()
        draw_main_screen(now, alarm_set, alarm_hour, alarm_minute)

        # Sensor controls LED
        if sensor.is_pressed:
            leds.set_color('LEFT', 'GREEN')
            leds.set_color('RIGHT', 'GREEN')
        else:
            leds.all_off()

        # Buttons
        if btn.enter:
            alarm_set = not alarm_set
            msg = "Alarm EIN" if alarm_set else "Alarm AUS"
            draw_centered_text(50, msg, font_small)
            time.sleep(1)
            # redraw main screen after status
            now = get_local_time()
            draw_main_screen(now, alarm_set, alarm_hour, alarm_minute)
        elif btn.backspace:
            draw_centered_text(50, "Beende Programm...", font_small)
            time.sleep(1)
            screen.clear()
            screen.update()
            exit(0)
        elif btn.left or btn.right or btn.up or btn.down:
            alarm_hour, alarm_minute = set_alarm_time(alarm_hour, alarm_minute)
            alarm_set = True
            time.sleep(0.5)

        # Alarm check
        if alarm_set and now.hour == alarm_hour and now.minute == alarm_minute:
            ring_alarm()
            alarm_set = False

        time.sleep(1)

if __name__ == '__main__':
    main()
