#define BLYNK_TEMPLATE_ID "TMPL3V5WOMIDO"
#define BLYNK_TEMPLATE_NAME "Traffic Light"
#define BLYNK_AUTH_TOKEN "QhGZeAeyMK21RWd3NBwgWnXnBoQmFp1C"
#include <SevSeg.h>
#include <WiFi.h>
#include <BlynkSimpleEsp32.h>


char ssid[] = "Noname";
char pass[] = "error404";

BlynkTimer timer;
SevSeg sevseg;

int green = 18, yellow = 19, red = 23;
int green2 = 33, yellow2 = 32, red2 = 25;

char traffic = 'L';
int phase = 0;
unsigned long previousTime = 0;

void setup() {
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);
timer.setInterval(1000L, sendBlynkStatus);
  pinMode(green, OUTPUT);
  pinMode(yellow, OUTPUT);
  pinMode(red, OUTPUT);

  pinMode(green2, OUTPUT);
  pinMode(yellow2, OUTPUT);
  pinMode(red2, OUTPUT);

  byte numDigits = 1;
  byte digitPins[] = {};
  byte segmentPins[] = {13, 14, 4, 2, 21, 22, 26};

  sevseg.begin(COMMON_CATHODE, numDigits, digitPins,
               segmentPins, true);
  sevseg.setBrightness(90);

  Serial.begin(9600);
  previousTime = millis();
}

void sendBlynkStatus() {
  Blynk.virtualWrite(V0, traffic == 'H' ? "HIGH" : "LOW");

  if (phase == 0) {
    Blynk.virtualWrite(V1, "GREEN");
    Blynk.virtualWrite(V2, "RED");
  }
  else if (phase == 1) {
    Blynk.virtualWrite(V1, "YELLOW");
    Blynk.virtualWrite(V2, "RED");
  }
  else {
    Blynk.virtualWrite(V1, "RED");
    Blynk.virtualWrite(V2, "GREEN");
  }

  Blynk.virtualWrite(V3, "OFF");
  Blynk.virtualWrite(V4, "OFF");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'H' || c == 'L')
      traffic = c;
  }

  unsigned long now = millis();
  unsigned long duration;

  if (phase == 0)
    duration = (traffic == 'H') ? 9000 : 5000;
  else if (phase == 1)
    duration = 2000;
  else
    duration = 3000;

  if (now - previousTime >= duration) {
    previousTime = now;
    phase = (phase + 1) % 3;
  }

  digitalWrite(green, phase == 0);
  digitalWrite(yellow, phase == 1);
  digitalWrite(red, phase == 2);

  digitalWrite(green2, phase == 2);
  digitalWrite(yellow2, LOW);
  digitalWrite(red2, phase != 2);

  if (phase == 0) {
    int remaining =
      (duration - (millis() - previousTime) + 999) / 1000;

    sevseg.setNumber(remaining);
  } else {
    sevseg.setNumber(0);
  }

  sevseg.refreshDisplay();

  Blynk.run();
timer.run();
}
