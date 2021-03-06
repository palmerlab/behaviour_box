EESchema Schematic File Version 2
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L LM358N U1
U 1 1 58CB77BC
P 3650 2200
F 0 "U1" H 3650 2400 50  0000 L CNN
F 1 "LM358N" H 3650 2000 50  0000 L CNN
F 2 "" H 3650 2200 50  0000 C CNN
F 3 "" H 3650 2200 50  0000 C CNN
	1    3650 2200
	-1   0    0    -1  
$EndComp
$Comp
L LM358N U1
U 2 1 58CB7839
P 4350 2000
F 0 "U1" H 4350 2200 50  0000 L CNN
F 1 "LM358N" H 4350 1800 50  0000 L CNN
F 2 "" H 4350 2000 50  0000 C CNN
F 3 "" H 4350 2000 50  0000 C CNN
	2    4350 2000
	0    -1   1    0   
$EndComp
$Comp
L R R1
U 1 1 58CB7BAE
P 2650 2950
F 0 "R1" V 2730 2950 50  0000 C CNN
F 1 "R" V 2650 2950 50  0000 C CNN
F 2 "" V 2580 2950 50  0000 C CNN
F 3 "" H 2650 2950 50  0000 C CNN
	1    2650 2950
	1    0    0    -1  
$EndComp
$Comp
L D D1
U 1 1 58CB7C23
P 2650 2250
F 0 "D1" H 2650 2350 50  0000 C CNN
F 1 "D" H 2650 2150 50  0000 C CNN
F 2 "" H 2650 2250 50  0000 C CNN
F 3 "" H 2650 2250 50  0000 C CNN
	1    2650 2250
	0    -1   1    0   
$EndComp
$Comp
L C C1
U 1 1 58CB7D91
P 5100 1750
F 0 "C1" H 5125 1850 50  0000 L CNN
F 1 "C" H 5125 1650 50  0000 L CNN
F 2 "" H 5138 1600 50  0000 C CNN
F 3 "" H 5100 1750 50  0000 C CNN
	1    5100 1750
	1    0    0    -1  
$EndComp
$Comp
L R R5
U 1 1 58CB7E09
P 5450 1750
F 0 "R5" V 5530 1750 50  0000 C CNN
F 1 "R" V 5450 1750 50  0000 C CNN
F 2 "" V 5380 1750 50  0000 C CNN
F 3 "" H 5450 1750 50  0000 C CNN
	1    5450 1750
	1    0    0    -1  
$EndComp
$Comp
L RTRIM R2
U 1 1 58CB81CC
P 4000 2650
F 0 "R2" V 4100 2550 50  0000 L CNN
F 1 "RTRIM" V 3900 2625 50  0000 L CNN
F 2 "" V 3930 2650 50  0000 C CNN
F 3 "" H 4000 2650 50  0000 C CNN
	1    4000 2650
	1    0    0    -1  
$EndComp
$Comp
L R R3
U 1 1 58CB8225
P 4450 2750
F 0 "R3" V 4530 2750 50  0000 C CNN
F 1 "R" V 4450 2750 50  0000 C CNN
F 2 "" V 4380 2750 50  0000 C CNN
F 3 "" H 4450 2750 50  0000 C CNN
	1    4450 2750
	0    1    1    0   
$EndComp
$Comp
L R R4
U 1 1 58CB8286
P 4950 2550
F 0 "R4" V 5030 2550 50  0000 C CNN
F 1 "R" V 4950 2550 50  0000 C CNN
F 2 "" V 4880 2550 50  0000 C CNN
F 3 "" H 4950 2550 50  0000 C CNN
	1    4950 2550
	0    1    1    0   
$EndComp
Wire Wire Line
	4000 1350 4000 1900
Connection ~ 4000 1900
Wire Wire Line
	2650 2400 2650 2800
Connection ~ 2650 2600
Wire Wire Line
	2650 2100 2650 1050
Wire Wire Line
	2650 1050 5300 1050
Wire Wire Line
	5300 1050 5300 1450
Wire Wire Line
	5100 1450 5450 1450
Wire Wire Line
	5100 1450 5100 1600
Wire Wire Line
	5450 1450 5450 1600
Connection ~ 5300 1450
Wire Wire Line
	5100 1900 5100 2050
Wire Wire Line
	5100 2050 5450 2050
Wire Wire Line
	5450 2050 5450 1900
Wire Wire Line
	4250 1700 4250 1050
Connection ~ 4250 1050
Wire Wire Line
	4650 1900 4900 1900
Wire Wire Line
	4900 1900 4900 2200
Wire Wire Line
	4900 2200 5300 2200
Connection ~ 5300 2050
Connection ~ 5300 2200
Wire Wire Line
	3350 2200 3200 2200
Wire Wire Line
	3200 2200 3200 2600
Wire Wire Line
	3200 2600 2650 2600
Wire Wire Line
	4000 2300 3950 2300
Wire Wire Line
	4000 2300 4000 2500
Wire Wire Line
	4000 2800 4000 3100
Wire Wire Line
	4000 3100 2650 3100
Wire Wire Line
	4000 2400 4200 2400
Wire Wire Line
	4200 2400 4200 2750
Wire Wire Line
	4200 2750 4300 2750
Connection ~ 4000 2400
Wire Wire Line
	5300 2750 4600 2750
Connection ~ 5300 2750
Wire Wire Line
	5300 2550 5100 2550
Connection ~ 5300 2550
Wire Wire Line
	4800 2550 4300 2550
Wire Wire Line
	4300 2550 4300 2300
Wire Wire Line
	4300 2300 4050 2300
Wire Wire Line
	4050 2300 4050 2100
Wire Wire Line
	4050 2100 3950 2100
Wire Wire Line
	5300 2050 5300 3200
Wire Wire Line
	4600 2250 4600 2550
Connection ~ 4600 2550
$Comp
L Earth #PWR01
U 1 1 58CB922B
P 5300 3200
F 0 "#PWR01" H 5300 2950 50  0001 C CNN
F 1 "Earth" H 5300 3050 50  0001 C CNN
F 2 "" H 5300 3200 50  0000 C CNN
F 3 "" H 5300 3200 50  0000 C CNN
	1    5300 3200
	1    0    0    -1  
$EndComp
$Comp
L +5V #PWR02
U 1 1 58CB9443
P 4000 1350
F 0 "#PWR02" H 4000 1200 50  0001 C CNN
F 1 "+5V" H 4000 1490 50  0000 C CNN
F 2 "" H 4000 1350 50  0000 C CNN
F 3 "" H 4000 1350 50  0000 C CNN
	1    4000 1350
	1    0    0    -1  
$EndComp
Wire Wire Line
	4500 1400 4450 1400
Wire Wire Line
	4450 1400 4450 1700
Wire Wire Line
	3750 1900 4050 1900
NoConn ~ 4350 2300
NoConn ~ 3750 2500
Entry Wire Line
	4500 1400 4600 1500
Wire Wire Line
	4600 2250 4800 2250
Entry Wire Line
	4800 2250 4900 2350
Text Label 4900 2350 0    60   ~ 0
signal_in
Text Label 4600 1500 0    60   ~ 0
signal_out
$EndSCHEMATC
