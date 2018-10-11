const char CMD_TRIGGERED = 'T';
const char CMD_ACTIVE = 'A';
const char CMD_OFF = 'O';

char CURRENT_CMD;
char NEW_CMD;
int delay_amt = 0;

void setup() {
   Serial.begin(9600);
   pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
 // send data only when you receive data: 
  if (Serial.available() > 0) {
    CURRENT_CMD = Serial.readString().charAt(0);
    
    switch (CURRENT_CMD) {
      case CMD_TRIGGERED:
        trigger();
        break;
      case CMD_ACTIVE:
        active();
        break;
      case CMD_OFF:
        off();
        break;
      default:
        off();
        break;
    }
    Serial.flush(); 
  }  
}

void trigger() {
  digitalWrite(LED_BUILTIN, HIGH);
}

void active() {
  digitalWrite(LED_BUILTIN, LOW);
}

void off() {
  digitalWrite(LED_BUILTIN, LOW);
}
