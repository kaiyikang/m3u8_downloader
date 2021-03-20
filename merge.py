import os
from natsort import natsorted
from tqdm import tqdm

path='.\\temp'
ts_files=[path+'\{}.ts'.format(str(ij)) for ij in natsorted([int(str_1[:str_1.find('.')]) for str_1 in os.listdir(path)])]
pbar = tqdm(total=len(ts_files))

for str_2 in ts_files:
    pbar.update(1)
    with open(file=str_2,mode='rb') as f:
        content=f.read()
    with open(file='./龙王传说.mp4',mode='ab') as fp:
        fp.write(content)
