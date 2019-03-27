import os
import numpy as np
import matplotlib.pyplot as plt
import math

if __name__ == "__main__":
	dir = "loss/maestro_02/"

	for filename in os.listdir(dir):
		name , ext= os.path.splitext(filename)
		print('------------')
		print(filename)
		print('------------')

		data = np.load(dir + filename)
		x = range(data.shape[0])

		print(data)
		print("nb epochs : %d" %data.shape[0])


		# if math.isnan(data[2]) == False:
		# 	data[2] = (data[1] + data[3]) / 2
		#
		# if data[2] > 0:
		# 	data[2] = 0

		# print(data)

		plt.plot(x, data)

		plot_name = "plot/" + name + ".png"
		plt.savefig(fname=plot_name,format="png")
		plt.close()

	print('DONE')
