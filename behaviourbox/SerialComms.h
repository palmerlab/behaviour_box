/*----------------------------------------------++
||                  Serial Coms                 ||
++----------------------------------------------*/

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

int getSepIndex(String input, char separator) {
    /*
      Returns the index of the separator character
      in a string.
    */

    char c = 1;
    int i = 0;

    while (c != 0) {
        c = input[i];
        if (c == separator){
            return i;
        }
        i ++;
    }
    return 0;
}

int UpdateGlobals(String input) {
    /*
    This is a big ugly function which compares the
    input string to the names of variables that I have
    stored in memory; This is very much not the `C`
    way to do things...

    I think this could be a hash table. I haven't
    learned enough about hash table implementation
    yet and I know this works, so for the moment:
    *If it ain't broke*...
    */

    // sep is the index of the ':' character
    int sep = getSepIndex(input, ':');

    if (sep) {

        String variable_name = input.substring(0,sep);
        String variable_value = input.substring(sep+1);

        Serial.print("\t#");
        Serial.print(variable_name);
        Serial.print(":");
        Serial.println(variable_value);

        // input before seperator?
        // lickThres
        if (variable_name == "lickThres") {
                lickThres = variable_value.toInt();
                Serial.print("\tlickThres:");
                Serial.println(lickThres);
                return 1;
        }        // mode
        else if (variable_name == "mode") {
                mode = variable_value[0];
                Serial.print("\tmode:");
                Serial.println(mode);
                return 1;
        }
        // trialType
        else if (variable_name == "trialType") {
                trialType = variable_value[0];
                Serial.print("\ttrialType:");
                Serial.println(trialType);
                return 1;
        }
        // minlickCount
        else if (variable_name == "minlickCount") {
                minlickCount = variable_value.toInt();
                Serial.print("\tminlickCount:");
                Serial.println(minlickCount);
                return 1;
        }

        // t_noLickPer
        else if (variable_name == "t_noLickPer") {
                t_noLickPer = variable_value.toInt();
                Serial.print("\tt_noLickPer:");
                Serial.println(t_noLickPer);
                return 1;
        }
        // timeout
        else if (variable_name == "timeout") {
                timeout = variable_value.toInt();
                Serial.print("\ttimeout:");
                Serial.println(timeout);
                return 1;
        }

        // reward_nogo
        else if (variable_name == "reward_nogo") {
                reward_nogo = bool(variable_value.toInt());
                Serial.print("\treward_nogo:");
                Serial.println(reward_nogo);
                return 1;
        }

        // lickTrigReward
        else if (variable_name == "lickTrigReward") {
                lickTrigReward = bool(variable_value.toInt());
                Serial.print("\tlickTrigReward:");
                Serial.println(lickTrigReward);
                return 1;
        }

        // t_stimONSET
        else if (variable_name == "t_stimONSET") {
                t_stimONSET = variable_value.toInt();
                Serial.print("\tt_stimONSET:");
                Serial.println(t_stimONSET);
                return 1;
        }

        // t_stimDUR
        else if (variable_name == "t_stimDUR") {
                t_stimDUR = variable_value.toInt();
                Serial.print("\tt_stimDUR:");
                Serial.println(t_stimDUR);
                return 1;
        }

        // t_rewardDEL
        else if (variable_name == "t_rewardDEL") {
                t_rewardDEL = variable_value.toInt();
                Serial.print("\tt_rewardDEL:");
                Serial.println(t_rewardDEL);
                return 1;
        }

        // t_rewardDUR
        else if (variable_name == "t_rewardDUR") {
                t_rewardDUR = variable_value.toInt();
                Serial.print("\tt_rewardDUR:");
                Serial.println(t_rewardDUR);
                return 1;
        }

        // t_trialDUR
        else if (variable_name == "t_trialDUR") {
                t_trialDUR = variable_value.toInt();
                Serial.print("\tt_trialDUR:");
                Serial.println(t_trialDUR);
                return 1;
        }

        // waterVol
        else if (variable_name == "waterVol") {
                waterVol = variable_value.toInt();
                Serial.print("\twaterVol:");
                Serial.println(waterVol);
                return 1;
        }

        // punish_tone
        else if (variable_name == "punish_tone") {
                punish_tone = variable_value.toInt();
                Serial.print("\tpunish_tone:");
                Serial.println(punish_tone);
                return 1;
        }

        // debounce
        else if (variable_name == "debounce") {
                debounce = variable_value.toInt();
                Serial.print("\tdebounce:");
                Serial.println(debounce);
                return 1;
        }

        // audio
        else if (variable_name == "audio") {
                audio = variable_value.toInt();
                Serial.print("\taudio:");
                Serial.println(audio);
                return 1;
        }
   }
   return 0;
}
