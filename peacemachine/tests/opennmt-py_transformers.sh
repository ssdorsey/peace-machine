python /home/spenc/Dropbox/OpenNMT-py/tools/learn_bpe.py -s 32000 < train_es.txt > bpe-codes.src -v

python /home/spenc/Dropbox/OpenNMT-py/tools/apply_bpe.py -c bpe-codes.src < train_es.txt > train.src
python /home/spenc/Dropbox/OpenNMT-py/tools/apply_bpe.py -c bpe-codes.src < valid_es.txt > valid.src
python /home/spenc/Dropbox/OpenNMT-py/tools/apply_bpe.py -c bpe-codes.src < test_es.txt > test.src

python /home/spenc/Dropbox/OpenNMT-py/tools/learn_bpe.py -s 32000 < train_en.txt > bpe-codes.tgt -v

python /home/spenc/Dropbox/OpenNMT-py/tools/apply_bpe.py -c bpe-codes.tgt < train_en.txt > train.tgt
python /home/spenc/Dropbox/OpenNMT-py/tools/apply_bpe.py -c bpe-codes.tgt < valid_en.txt > valid.tgt
python /home/spenc/Dropbox/OpenNMT-py/tools/apply_bpe.py -c bpe-codes.tgt < test_en.txt > test.tgt

onmt_preprocess -train_src train.src -train_tgt train.tgt -valid_src valid.src -valid_tgt valid.tgt -save_data processed/ -src_seq_length 50 -tgt_seq_length 50 -seed 100 -log_file log.preprocess -num_threads 12 -shard_size 300000

tar -I pigz -cf /media/spenc/D/processed.tar.gz processed

