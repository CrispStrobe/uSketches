#include <Arduino.h>
#include "AudioTools.h"
#include "FileSystems.h"
#include "espeak.h"

// === Audio über PWM auf GPIO18 ===
PWMAudioOutput pwm;
const bool load_english = false;
ESpeak espeak(pwm, load_english);

// === Pins ===
constexpr int PIR_PIN = 15;
constexpr int TRIG_PIN = 16;
constexpr int ECHO_PIN = 17;
constexpr int BUTTON_PIN = 19;  // Taster zwischen GPIO19 und GND

// === Messkonfiguration ===
constexpr unsigned long MEASURE_INTERVAL_MS = 200;
constexpr unsigned long CHECK_INTERVAL_MS = 1000;
constexpr float DISTANCE_THRESHOLD_PERCENT = 0.10;

unsigned long lastMeasureTime = 0;
unsigned long lastCheckTime = 0;

bool recentMotion = false;
float lastDistance = -1;
float minDistance = -1;
float maxDistance = -1;

void setup() {
  Serial.begin(115200);

  pinMode(PIR_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Sprachdaten laden
  espeak.add("/mem/data/de_dict", espeak_ng_data_de_dict, espeak_ng_data_de_dict_len);
  espeak.add("/mem/data/lang/de", espeak_ng_data_lang_gmw_de, espeak_ng_data_lang_gmw_de_len);

  espeak.begin();
  espeak.setVoice("de");

  // Audio konfigurieren
  auto info = espeak.audioInfo();
  auto cfg = pwm.defaultConfig();
  cfg.sample_rate = info.sample_rate;
  cfg.channels = info.channels;
  cfg.bits_per_sample = info.bits_per_sample;
  cfg.start_pin = 18;
  pwm.begin(cfg);

  espeak.say("Systemstart abgeschlossen.");
}

long readDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  long distance = duration * 0.034 / 2;
  return distance;
}

void loop() {
  unsigned long now = millis();

  // === Button gedrückt?
  if (digitalRead(BUTTON_PIN) == LOW) {
    delay(20); // einfache Entprellung
    while (digitalRead(BUTTON_PIN) == LOW); // gedrückt halten abwarten

    long currentDistance = readDistanceCM();
    char msg[64];
    snprintf(msg, sizeof(msg), "%s, %ld Zentimeter.",
             recentMotion ? "Ja" : "Nein", currentDistance);
    Serial.print("[Taster] ");
    Serial.println(msg);
    espeak.say(msg);
  }

  // === Regelmäßige Messung alle 200ms ===
  if (now - lastMeasureTime >= MEASURE_INTERVAL_MS) {
    lastMeasureTime = now;

    bool motion = digitalRead(PIR_PIN);
    long distance = readDistanceCM();

    if (motion) recentMotion = true;
    if (minDistance < 0 || distance < minDistance) minDistance = distance;
    if (maxDistance < 0 || distance > maxDistance) maxDistance = distance;

    Serial.print("[Messung] PIR: ");
    Serial.print(motion ? "1" : "0");
    Serial.print(" | Entfernung: ");
    Serial.print(distance);
    Serial.println(" cm");
  }

  // === Check alle 1 Sekunde: Begrüßung bei Bewegung oder Abstandänderung ===
  if (now - lastCheckTime >= CHECK_INTERVAL_MS) {
    lastCheckTime = now;

    bool distanceChanged = false;
    if (lastDistance >= 0 && (maxDistance - minDistance) > (lastDistance * DISTANCE_THRESHOLD_PERCENT)) {
      distanceChanged = true;
    }

    if (recentMotion || distanceChanged) {
      espeak.say("Hallo! Herzlich Willkommen!");
    }

    lastDistance = (minDistance + maxDistance) / 2.0;
    recentMotion = false;
    minDistance = -1;
    maxDistance = -1;
  }
}
