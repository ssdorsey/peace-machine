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

# onmt_train -data processed/ -save_model models/sp_transformer \
#         -layers 6 -rnn_size 512 -word_vec_size 512 -transformer_ff 2048 -heads 8  \
#         -encoder_type transformer -decoder_type transformer -position_encoding \
#         -train_steps 100000  -max_generator_batches 2 -dropout 0.1 \
#         -batch_size 4096 -batch_type tokens -normalization tokens  -accum_count 2 \
#         -optim adam -adam_beta2 0.998 -decay_method noam -warmup_steps 8000 -learning_rate 2 \
#         -max_grad_norm 0 -param_init 0  -param_init_glorot \
#         -label_smoothing 0.1 -valid_steps 5000 -save_checkpoint_steps 5000 \
#         -world_size 8 -gpu_ranks 0 1 2 3 4 5 6 7 -log_file models/log.train \
#         -tensorboard -tensorboard_log_dir models/

# onmt_translate -model models/sp_transformer_step_100000.pt -src test.src -output test_predictions.src -replace_unk -gpu 0

# sed -i 's/@@ //g' test_predictions.src

# perl /home/spenc/Dropbox/OpenNMT-py/tools/multi-bleu.perl test.tgt < test_predictions.src
