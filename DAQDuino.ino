/*
* Arduiono DAQ: Takes temperature from an SHT71 sensor and voltage
* from one analog channel of the Arduino.
*/

#include <Sensirion.h>


const byte dataPin =  2;                 // SHTxx serial data
const byte sclkPin =  3;                 // SHTxx serial clock
const byte ledPin  = 13;                 // Arduino built-in LED
const unsigned long TRHSTEP   = 900UL;   // Sensor query period
unsigned long trhMillis = 0;             // Time interval tracking
int d = 1;                                // us delay for serial prints

Sensirion sht = Sensirion(dataPin, sclkPin);

unsigned int rawData;
unsigned int val;

byte ledState = 0;
byte measActive = false;

//Setup 
void setup() {
  pinMode(A0, INPUT);
  pinMode(ledPin, OUTPUT);
  ledState = 1; 
  digitalWrite(ledPin, ledState);  // Turn LED when measuring
  sht.writeSR(LOW_RES);        // Set sensor to low resolution (12bit)
  Serial.begin(9600);
  delay(15);                   // Wait >= 11 ms before first cmd
}// End setup

// Main loop
void loop() {
  unsigned long curMillis = millis();          // Get current time
  
  if(Serial.available()) {
    
    int signal = Serial.read();
    
    if(signal == 119) {// Python code sends 'w' to tell Arduino to start and send 
                       // measurements 
    
      if (curMillis - trhMillis >= TRHSTEP) {      // Time for new measurements?
        measActive = true;
        sht.meas(TEMP, &rawData, NONBLOCK);        // Start temp measurement
        trhMillis = curMillis;
      } // End if (checking for new measurement start)
      
      val = analogRead(A0);
      
      if (measActive && sht.measRdy()) {           // Check measurement status
          measActive = false;                      // Deactivate sensor
          logData();
      }//End if (retrieving temperature measurement)

    }//End if (sending measurement)
  }//End if (Serial.available)
}//End of loop
  
  void logData() {
  Serial.println( rawData );  delayMicroseconds(d);
  Serial.println( val );  delayMicroseconds(d);
}
