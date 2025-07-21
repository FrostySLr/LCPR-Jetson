int vldPin = 2;
int detectionStatus;

void setup() {
  pinMode(vldPin, INPUT_PULLUP);
  Serial.begin(9600);
}

void loop() {
  detectionStatus = digitalRead(vldPin);

  if (detectionStatus == LOW) {
    Serial.println("No Vehicle Detected");
  } else {
    Serial.println("Vehicle Detected");
  }

  delay(1000); # delay for stability
}