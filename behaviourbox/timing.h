/*----------------------------------------------++
||                  Timing                      ||
++----------------------------------------------*/

long t_since(unsigned long t_init){
    // The time since t_init:
    //   + is less than 0 before the trial starts
    //   + is greater than 0 after the start of trial

    return (long) millis() - t_init;
}