import os
from natsort import natsorted
from tqdm import tqdm


def ts_merge(path='.\\temp'):
    ts_files=[path+'\{}.ts'.format(str(ij)) for ij in natsorted([int(str_1[:str_1.find('.')]) for str_1 in os.listdir(path)])]
    pbar = tqdm(total=len(ts_files))
    
    for ts_files in ts_files:
        pbar.update(1)
        with open(file=ts_files,mode='rb') as f:
            content=f.read()
        with open(file='./龙王传说.mp4',mode='ab') as fp:
            fp.write(content)

if __name__ == "__main__":
    ts_merge()