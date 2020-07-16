onmt_train -data processed/ -save_model models/sp_transformer \
        -layers 6 -rnn_size 512 -word_vec_size 512 -transformer_ff 2048 -heads 8  \
        -encoder_type transformer -decoder_type transformer -position_encoding \
        -train_steps 100000  -max_generator_batches 2 -dropout 0.1 \
        -batch_size 4096 -batch_type tokens -normalization tokens  -accum_count 2 \
        -optim adam -adam_beta2 0.998 -decay_method noam -warmup_steps 8000 -learning_rate 2 \
        -max_grad_norm 0 -param_init 0  -param_init_glorot \
        -label_smoothing 0.1 -valid_steps 5000 -save_checkpoint_steps 5000 \
        -world_size 8 -gpu_ranks 0 1 2 3 4 5 6 7 -log_file models/log.train \
        -tensorboard -tensorboard_log_dir models/

onmt_translate -model models/sp_transformer_step_100000.pt -src test.src -output test_predictions.src -replace_unk -gpu 0

sed -i 's/@@ //g' test_predictions.src

perl /home/spenc/Dropbox/OpenNMT-py/tools/multi-bleu.perl test.tgt < test_predictions.src