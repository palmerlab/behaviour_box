import os
import numpy as np
import sys
import msvcrt as m
import time
import datetime

def random_block(
	block = ['0Hz', '5Hz', '10Hz', '25Hz', '50Hz', '100Hz'],
	repeats = 10):
	
	date = datetime.date.today().strftime('%y%m%d')
	DATADIR = os.path.join("C:\\DATA\\Andrew\\DATA", date)
	
	if not	os.path.isdir(DATADIR):
		os.mkdir((DATADIR))
	
	filename = "F_blocks" +date + ".txt"
	outfile = os.path.join(DATADIR, filename)
	
	with open(outfile, 'a') as f:
		f.write(time.strftime("%H:%M:%S"))
		f.write("\t---new set---")
		
		r = 0
		input = ""
		
		while True:
			np.random.shuffle(block)
			
			f.write(time.strftime("%H:%M:%S"))
			for i in xrange(len(block)):
				f.write('\t')
				f.write("%03d" %int(block[i][:-2]))
			f.write('\n')
			
			print "block", r, block, "\r",
			r +=1
			input = m.getch()
			#print input
			if input == "\x03" or input == 'q':
				print "\nbroken at repeats =", r
				break


if __name__ == "__main__":
	try:
		random_block(sys.argv[1])
	except:
		print "---"
		print "block = ['0Hz', '5Hz', '10Hz', '25Hz', '50Hz', '100Hz']"
		print "Press any key for next block... `Ctrl-c` to quit"
		print "---"
		random_block()