// new program with stop

class Device {
    // Class Member Variables. These are initialized at startup
    int flexionValve;      // the number of the valve pins
    int extensionValve;
    int flexionLed;
    int extensionLed;
    int flexTime;    
    int extTime;    
    int remainingReps;
    int fibreValue;
    int intensity;

    int inFlextionState;                 // ledState used to set the LED
    unsigned long previousMillis;   // will store last time LED was updated

  public: // Constructor - and initializes the member variables and state
    Device(int flexPin, int extPin, int flexLedPin, int extLedPin, int fibrePin, int flextionTime, int extensionTime, int intensity, int repetitions) {
      flexionValve = flexPin; //valve pins
      extensionValve = extPin;
      pinMode(flexionValve, OUTPUT); // can do in setup?
      pinMode(extensionValve, OUTPUT);

      flexionLed = flexLedPin; //led pins
      extensionLed = extLedPin;
      pinMode(flexionLed, OUTPUT);
      pinMode(extensionLed, OUTPUT);
      //pinMode(fibrePin, A0); // probably an A0 or somthing

      flexTime = flextionTime;
      extTime = extensionTime;
      intensity = 255;//intensity;
      remainingReps = repetitions;

      inFlextionState = LOW;
      previousMillis = 0;
      //Serial.println("madeA:");
    }

    int Update() {// return the lastest fibre optics (1 fibre line

      //if there are remaining repetitons // else return void to destroy device?
      if (remainingReps > 0) {
        unsigned long currentMillis = millis();
        

        if ((inFlextionState == HIGH) && (currentMillis - previousMillis >= flexTime)) { // time to change?
          //analogWrite(3, 100);
          //delay (1000);
          //analogWrite(3, 0);
          //Serial.print("opening: Reps remainign");
          //Serial.println(remainingReps);
          
          //analogWrite(flexionValve, 0);  // Extend wrist
          //analogWrite(3, 255);
          digitalWrite(flexionValve, LOW);  // Extend wrist
          digitalWrite(extensionValve, HIGH);
          digitalWrite(flexionLed, LOW);
          digitalWrite(extensionLed, HIGH);
          
          inFlextionState = LOW;
          previousMillis = currentMillis;  // Remember the time
        }

        else if ( (inFlextionState == LOW) && ((currentMillis - previousMillis >= extTime) || (previousMillis == 0)) ) {
          //Serial.print("closeing: Reps remainign");
          //Serial.println(remainingReps);
          //analogWrite(flexionValve, intensity);  // Flex wrist
          //analogWrite(3, 0);
          digitalWrite(flexionValve, HIGH);  // Flex wrist
          digitalWrite(extensionValve, LOW);
          digitalWrite(flexionLed, HIGH); // show leds
          digitalWrite(extensionLed, LOW);

          if (previousMillis != 0) {
            remainingReps--;
          }
          inFlextionState = HIGH;
          previousMillis = currentMillis;   // Remember the time
        }
        if(flexionValve == 2){
          fibreValue = analogRead(A0);
        }
        if(flexionValve == 4){
          fibreValue = analogRead(A1);
        }
        
        
        return fibreValue; // only return fibre every 50ms? from here? may not be at the same time

      } else { // finishe
        //analogWrite(flexionValve, 0);  // Close both wrists
        //analogWrite(extensionValve, 0);
        Stop();
        // digitalWrite(flexionValve, LOW);  // Flex wrist
        // digitalWrite(extensionValve, LOW);
        // digitalWrite(flexionLed, LOW); // and leds
        // digitalWrite(extensionLed, LOW);
        return -1; // no reps remaning %return everything and then sort
      }
    }
    void Stop() {
      digitalWrite(flexionValve, LOW);  // Flex wrist
      digitalWrite(extensionValve, LOW);
      digitalWrite(flexionLed, LOW); // and leds
      digitalWrite(extensionLed, LOW);
    }
};

//Data Received From Serial
String inputString;  // Full string from control panel
int inputLength;
String whichDevice;
String flexTime;
String extTime;
String intensity;
String repetitions;

int fibreA = -1;
int fibreB = -1;

int serialInterval = 5;
unsigned long previousMillisSerial = 0;
unsigned long startMillis;

boolean runningA = false;
boolean runningB = false;

Device* A = nullptr;
Device* B = nullptr;

void setup()
{
  Serial.begin(115200);
  // Serial1.begin(115200); // for debugging
  // try turnig the leds off (one is on)
  //pinMode(2, OUTPUT); // power off valves
  //pinMode(3, OUTPUT);
  //pinMode(4, OUTPUT);
  //pinMode(5, OUTPUT);
  //analogWrite(2, 0);
  //analogWrite(3, 0);
  //analogWrite(4, 0);
  //analogWrite(5, 0);

  pinMode(7, OUTPUT); // power off internal leds
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  digitalWrite(7, LOW);
  digitalWrite(8, LOW);
  digitalWrite(9, LOW);
  digitalWrite(10, LOW);

  pinMode(11, OUTPUT); // power off external leds
  pinMode(12, OUTPUT);
  digitalWrite(11, LOW);
  digitalWrite(12, LOW);
  startMillis = millis();
}

void loop()
{
  if (Serial.available() > 0) {  //  check for sererial

    inputString = Serial.readStringUntil('\n');
    inputLength = inputString.length();
    Serial.println(inputString);

    if (inputString.charAt(0) == '-') { // stop signal
      if (inputString.charAt(2) == 'A') {
        A->Stop();
        runningA = false;
        Serial.print("stoppedA:");
        Serial.println(millis()-startMillis);
        fibreA = -1;
        
      } else if(inputString.charAt(2) == 'B') {
        B->Stop();
        runningB = false;
        Serial.print("stoppedB:");
        Serial.println(millis()-startMillis);
        fibreB = -1;
      }


    } else { //send start signal
      int commaPositions[10]; // array for comma postions
      int commaCount = 0; // for the commaArray
      for (int i = 0; i < inputLength; i++) {
        if (inputString.charAt(i) == ',') {
          commaPositions[commaCount] = i;
          commaCount++;
          // Serial1.print("Comma at position: ");
          // Serial1.println(i);
        }
      }

      whichDevice = inputString.substring(0, commaPositions[0]);
      flexTime = inputString.substring(commaPositions[0] + 1, commaPositions[1]);
      extTime = inputString.substring(commaPositions[1] + 1, commaPositions[2]);
      intensity = inputString.substring(commaPositions[2] + 1, commaPositions[3]);
      repetitions = inputString.substring(commaPositions[3] + 1, inputLength);
      if (0) { // change to serial debug or serial 1
        Serial.print("device: ");  
        Serial.print(whichDevice);
        Serial.print(", flexTime: ");
        Serial.print(flexTime);
        Serial.print(", extTime: ");
        Serial.print(extTime);
        Serial.print(", intensity: ");
        Serial.print(intensity);
        Serial.print(", repetitions: ");
        Serial.println(repetitions);
      }
  
      if (whichDevice.equals("A")) {
        if (runningA) {
          Serial.println("alreadyRunning");
        } else {
          A = new Device(2, 3, 7, 8, 0, flexTime.toInt(), extTime.toInt(), intensity.toInt(), repetitions.toInt());
          runningA = true;
          Serial.print("madeA:");
          Serial.println(millis()-startMillis);
          //analogWrite(3, 100);
          //delay (1000);
          //analogWrite(3, 0);
        }

      } else if (whichDevice.equals("B")) {
        if (runningB) {
          Serial.println("alreadyRunning");
        } else {
          B = new Device(4, 5, 9, 10, 1, flexTime.toInt(), extTime.toInt(), intensity.toInt(), repetitions.toInt());
          runningB = true;
          Serial.print("madeB:");
          Serial.println(millis()-startMillis);
        }
      }
    }
  

    //inputString = "";// reset the input
  }
  if (runningA) {
    fibreA = A->Update(); // fibre is return value or -1 in which case destroy and created = false
    if (fibreA == -1) { // device finished
      //destroy object?
      runningA = false;
      Serial.print("stoppedA:");
      Serial.println(millis()-startMillis);
    }
  }

  if (runningB) {
    fibreB = B->Update(); // fibre is return value or -1 in which case destroy and created = false
    if (fibreB == -1) { // device finished
      //destroy object?
      runningB = false;
      Serial.print("stoppedB:");
      Serial.println(millis()-startMillis);
    }
  }

  unsigned long currentMillis = millis(); // put in class
  if (currentMillis - previousMillisSerial >= serialInterval) { // serial feedback every 50ms
    previousMillisSerial = currentMillis;
      Serial.print("time:");
      Serial.print(currentMillis - startMillis);
      Serial.print(", A:");
      Serial.print(fibreA);
      Serial.print(", B:");
      Serial.println(fibreB);
  }
}
