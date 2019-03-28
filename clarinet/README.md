# ClariNet
A Pytorch Implementation of ClariNet (Mel Spectrogram --> Waveform)

Original code from [Sungwon Kim](https://github.com/ksw0306) --> [ClariNet](https://github.com/ksw0306/ClariNet)


# Requirements

- PyTorch                       0.4.0
- Python                        3.6 
- Librosa                       0.6.3
- anaconda                      2018.12                  
- pretty_midi                   0.2.8
- mido			      1.2.8
- matplotlib                    2.2.3  
- py-midi                       1.2.5    

# Installation
- Install anaconda3 : https://www.anaconda.com/distribution/#download-section choose command line installer for python 3.7 then run the script and follow the instructions
- create and set up a pytorch conda environment :
-`$ conda create --name pytorch   
$ source activate pytorch
$ conda install pytorch torchvision cudatoolkit=8.0 -c pytorch
$ conda install -c anaconda conda
$ conda update -n base -c defaults conda
$ conda install -c conda-forge librosa
$ conda update librosa
$ conda install -c roebel pretty_midi
$ conda install -c roebel mido `


# Examples (with maestro_bach dataset)

#### Step 1. Create Dataset

- The dataset directory must contains 2 directories (wav/ and midi/) with the filenames respectively in format [name].mid and [name].wav. For the Maestro_bach dataset download [here](https://drive.google.com/drive/folders/1sLqewIgdb93bNQqtPephimBznJCujdN1)
- To cut the dataset into small tracks (about 5s each): `python dataset.py [wav_dir] [midi_dir]` 
- To create the corresponding metadata.csv file (in_dir is the directory where the midi/ and wav/ directories are stored ie: maestro): `python3 create_csv.py --in_dir [in_dir]`

#### Step 2. Preprocessing (Preparing Mel Spectrogram)

`python preprocessing.py --in_dir  maestro --out_dir DATASETS/maestro --name maestro`

#### Step 3. Train Gaussian Autoregressive WaveNet (Teacher)

`python3 train.py --data_path ./DATASETS/maestro/ --save ./params/ --loss loss/maestro --log log/maestro --model_name maestro`

#### Step 4. Synthesize (Teacher)

`--load_step CHECKPOINT` : the # of the pre-trained *teacher* model's global training step (also depicted in the trained weight file)

`python3 synthesize.py --model_name maestro --num_blocks 4 --num_layers 6 --load_step CHECKPOINT --data_path DATASETS/maestro/ --sample_path samples/ --load params/ `

#### Step 5. Train Gaussian Inverse Autoregressive Flow (Student)

`--teacher_name (YOUR TEACHER MODEL'S NAME)`

`--teacher_load_step CHECKPOINT` : the # of the pre-trained *teacher* model's global training step (also depicted in the trained weight file)

`--KL_type qp` : Reversed KL divegence KL(q||p)  or `--KL_type pq` : Forward KL divergence KL(p||q)

`python train_student.py --model_name wavenet_gaussian_student --teacher_name wavenet_gaussian --teacher_load_step 10000 --batch_size 4 --num_blocks_t 4 --num_layers_t 6 --num_layers_s 6 --KL_type qp`

`python3 train_student.py --model_name maestro_student --teacher_name maestro --teacher_load_step CHECKPOINT --batch_size 4 --num_blocks_t 4 --num_layers_t 6 --num_layers_s 6 --KL_type qp --data_path DATASETS/maestro/ --sample_path samples/ --save params/ --load params/ --loss loss/maestro --log log/maestro`

#### Step 6. Synthesize (Student)

`--model_name (YOUR STUDENT MODEL'S NAME)`

`--load_step CHECKPOINT` : the # of the pre-trained *student* model's global training step (also depicted in the trained weight file)

`--teacher_name (YOUR TEACHER MODEL'S NAME)`

`--teacher_load_step CHECKPOINT` :  the # of the pre-trained *teacher* model's global training step (also depicted in the trained weight file)

`--KL_type qp` : Reversed KL divergence KL(q||p)  or `--KL_type pq` : Forward KL divergence KL(p||q)

`--temp TEMPERATURE` : Temperature (standard deviation) value implemented as z ~ N(0, 1 * TEMPERATURE)

`python synthesize_student.py --model_name maestro_student --load_step CHECKPOINT --teacher_name maestro --teacher_load_step CHECKPOINT --batch_size 4 --temp 0.7 --load params/`

# References


- ClariNet : [https://arxiv.org/abs/1807.07281](https://arxiv.org/abs/1807.07281)
- Clarinet implementation : [https://github.com/ksw0306/ClariNet]
