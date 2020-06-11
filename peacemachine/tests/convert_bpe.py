import time
from tqdm import tqdm
from bpemb import BPEmb

bpe = BPEmb(lang='multi', vs=320000, dim=300)

def encode_many(in_path, out_path):
    """
    encodes file with each sentence on one line
    :param in_path: string, path to file to encode
    :param out_path: string, path to file for saving 
    :return:
    """
    with open(in_path, 'r') as _file:
        all_lines = [ll.strip() for ll in _file.readlines()]

    with open(out_path, 'w') as _file:
        for al in tqdm(all_lines):
            _file.write(' '.join(bpe.encode(al)) + '\n')

if __name__ == "__main__":

    for ff in ['train', 'valid', 'test']:
        print('Starting: ', ff)
        for lang in ['es', 'en']:
            print('Starting: ', lang)
            _type = ff + '_' + lang

            encode_many(in_path=f'../data/translation/ES/{_type}.txt', 
            out_path=f'../data/translation/ES/{_type}_encoded_32.txt')
