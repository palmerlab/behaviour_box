// If you can read this:
// You shouldn't be touching these values
/*==============================================================================
||                           USER ADJUSTABLE VARIABLES
||                              adjust these HERE
++=============================================================================*/

unsigned long t_init;             // The internal clock start

/*==============================================================================
||                           TRIAL INPUT VARIABLES
||                               set over serial
++=============================================================================*/

bool somat_stim = false;
bool audit_stim = false;
bool go_trial   = false;

bool stimulus   = false;
bool light      = false;          // flags for opto-stimulation
bool light_resp = false;

/*==============================================================================
||                           SYSTEM OUTPUT VARIABLES
||                               not to be set
++=============================================================================*/

char response;                   // response, one of 'H', '-', 'f', 'R', 'e'
int N_to;                        // number of timeouts
bool reward;                     // true or false, signals if reward given
