/* -------------------------------------------------------++
||                  THE PROTOTYPES                        ||
++--------------------------------------------------------*/                  

String getSerialInput();

int getSepIndex(String input, char seperator = ":");


//definitions

String getSerialInput(){

    /*
      This function reads the data from the serial 
      connection and returns it as a string. 
      
      This is used later to update the values
    */
    String readString;
    
    while (Serial.available()) { 
        /* 1. delay to allow buffer to fill
           2. get one byte from serial buffer
           3. make the string readString 
       */
        
        delay(3);  
        char c = Serial.read();  
        readString += c; 
    }
    
    return readString;
}

int getSepIndex(String input, char seperator) {
    /*
      Returns the index of the seperator character
      in a string.
    */
    
    char c = 1;
    int i = 0;
   
    while (c != 0) {
        c = input[i];
        if (c == sep){ 
            return i; 
        }
        i ++;
    }
    return 0;
}
