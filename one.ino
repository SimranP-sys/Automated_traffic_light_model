
int green = 18;
int yellow = 19;
int red = 23;

int green2 = 33;
int yellow2 = 32;
int red2 = 25;

char traffic = 'L';
int phase = 0;
unsigned long previousTime = 0;

void setup() {
  pinMode(green, OUTPUT);
  pinMode(yellow, OUTPUT);
  pinMode(red, OUTPUT);

  pinMode(green2, OUTPUT);
  pinMode(yellow2, OUTPUT);
  pinMode(red2, OUTPUT);

  Serial.begin(9600);

  previousTime = millis();
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

  // Signal 1
  digitalWrite(green, phase == 0);
  digitalWrite(yellow, phase == 1);
  digitalWrite(red, phase == 2);

  // Opposite Signal 2
  digitalWrite(green2, phase == 2);
  digitalWrite(yellow2, phase == 1);
  digitalWrite(red2, phase == 0 || phase == 1);
}
