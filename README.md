# PFE_SampleRNN

## SampleRNN  Instructions for CREMI
### Installation procedure:
>- create a virtual environment :
> $ virtualenv [name]  
>- activate the virt env:
> $ source [nom_dossier]/bin/activate
> - install needed packages
> $ pip install theano
> $ pip install lasagne
> $ pip install --upgrade https://github.com/Lasagne/Lasagne/archive/master.zip  #(to upgrade to 0.2)
> $ pip install lib
> $ pip install matplotlib

### Running procedure on the music dataset:
>- `datasets/music` contains scripts to preprocess and build this dataset.
>- execute a "models/tier/tier.py" script with the command line described in **sampleRNN_ICLR2017/readme.md**
>- /!\ modify the option *gpu0* by *cuda*
>- Example:
>`THEANO_FLAGS=mode=FAST_RUN,device=cuda, floatX=float32 python -u models/two_tier/two_tier.py --exp BEST_2TIER --n_frames 64 --frame_size 16 --emb_size 256 --skip_conn False --dim 1024 --n_rnn 3 --rnn_type GRU --q_levels 256 --q_type linear --batch_size 128 --weight_norm True --learn_h0 True --which_set MUSIC`
---
- For the pygpu error: 
If you use `device=gpu0` instead of `device=cuda0`, it will use the  
older back-end, which does not need libgpuarray.

---
#### Useful tools:


##### Screen:

- Create screen session
`$ screen -S session_name` 
- Recup
`$ screen -r` 
- Detach
`$ screen -d`  	or	 ` ctrl-a d`
- To see running sessions
`$ screen -ls` 
 - Quit
`$ exit`

##### miscellaneous:
- cpu info
`$ lscpu`

- harware info
`$ lshw`

##### probleme ssh : 

This can happen when you move from one computer to another with the same .local directory. The following (from here) worked for me:

First delete ~/.theano which stores some theano compiled files. Then reinstall theano via pip uninstall theano; pip install --user theano. It also fixes the gensim install for some reason (which shows the same error upon importing). Perhaps gensim imports theano when it can?


