# Settings


| Flag      | Description |
| ----------- | ----------- |
| --eval_every_n   | Run test on the validation set and log metrics to tensorboard       |
| --report_every_n   | Update tensorboard with new values every n batches      |
| --save_every_n   | Save model checkpoint after every n batches        |
| --keep_every_n   | Remove older checkpoints and keep only last n models        |
| --batch_size   | Training batch size        |
| --eval_batch_size   | Testing batch size        |
| --eval_on_train   | Evaluate validation metrics on Training data?        |
| --no_eval_on_val   | Do not run validation tests during training?        |
| --data_seed   | Seed for random number generator in data loading        |
| --init_seed   | Seed for random number generator during PyTorch layers' initialization        |
| --model_seed   | Seed for the random number generator for models        |
| --num_batches   |  Stop training after `num_batches` steps       |
| --num_epochs   | Stop training after `num_epochs` epochs.        |
| --num_workers   | Number of workers for PyTorch  dataloader        |
| --num_eval_batches   | Only run validation on `num_eval_batches` number of batches|
