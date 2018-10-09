import os
import pandas as pd
import numpy as np
import sys



with open (sys.argv[1], 'r') as file:
	for line in file:
		if line != "\n":
			print(line[:-1])
file.close()


