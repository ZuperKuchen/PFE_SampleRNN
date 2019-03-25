import os
import numpy as np 
import matplotlib.pyplot as plt

#insert la ligne pour dire que c'est le main
if __name__ == "__main__":
	dir = "loss/essen30/"

	for filename in os.listdir(dir):
		name , ext= os.path.splitext(filename)

		data = np.load(dir + filename)
		x = range(data.shape[0])

		#juste pour verif que la ligne du dessus marche bien
		print(x)

		plt.plot(x, data)

		plot_name = "plot/" + name + ".png"
		plt.savefig(fname=plot_name,format="png") #peut être des quotes pour le format
		plt.close()

	print(DONE)
