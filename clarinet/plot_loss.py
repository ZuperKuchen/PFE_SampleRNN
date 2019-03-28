import os
import numpy as np
import matplotlib.pyplot as plt
import math

#script to plot loss of teacher or student train result
if __name__ == "__main__":
	dir = "loss/maestro_01/"

	for filename in os.listdir(dir):
		name , ext= os.path.splitext(filename)

		data = np.load(dir + filename)
		x = range(data.shape[0])

		plt.plot(x, data)

		plot_name = "plot/" + name + ".png"
		plt.savefig(fname=plot_name,format="png")
		plt.close()
