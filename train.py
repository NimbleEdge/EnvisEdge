from argparse import ArgumentParser
from fedrec.trainers.base_trainer import BaseTrainer

import torch
import yaml

from fedrec.utilities import registry
from fedrec.utilities.logger import NoOpLogger, TBLogger


def merge_config_and_args(config, args):
    arg_dict = vars(args)
    stripped_dict = {k: v for k, v in arg_dict.items() if (v is not None)}
    return {**config, **stripped_dict}


def main():
    parser = ArgumentParser()
    parser.add_argument("--config", type=str)

    parser.add_argument("--disable_logger",
                        dest='logger', action='store_false')
    parser.add_argument("--logdir", type=str, default=None)

    parser.add_argument("--weighted-pooling", type=str, default=None)

    # activations and loss
    parser.add_argument("--loss_function", type=str, default=None)
    parser.add_argument("--loss_weights", type=float, default=None)  # for wbce
    parser.add_argument("--loss_threshold", type=float,
                        default=0.0)  # 1.0e-7
    parser.add_argument("--round_targets",
                        dest='round_targets', action='store_true')

    # train Config
    parser.add_argument("--data_size", type=int, default=None)
    parser.add_argument("--eval_every_n", type=int, default=None)
    parser.add_argument("--report_every_n", type=int, default=None)
    parser.add_argument("--save_every_n", type=int, default=None)
    parser.add_argument("--keep_every_n", type=int, default=None)
    parser.add_argument("--batch_size", type=int, default=None)
    parser.add_argument("--eval_batch_size", type=int, default=None)
    parser.add_argument('--eval_on_train',
                        dest='eval_on_train', action='store_true')
    parser.add_argument('--no_eval_on_val',
                        dest='eval_on_val', action='store_false')
    parser.add_argument("--data_seed", type=int, default=None)
    parser.add_argument("--init_seed", type=int, default=None)
    parser.add_argument("--model_seed", type=int, default=None)
    parser.add_argument("--num_batches", type=int, default=None)
    parser.add_argument("--num_epochs", type=int, default=None)
    parser.add_argument("--num_workers", type=int, default=None)
    parser.add_argument("--num_eval_batches", type=int, default=None)

    parser.add_argument('--log_gradients',
                        dest='log_gradients', action='store_true')
    # gpu
    parser.add_argument('--pin_memory', dest='pin_memory', action='store_true')
    parser.add_argument("--devices", nargs="+", default=None, type=int)
    # store/load model
    parser.add_argument("--save-model", type=str, default=None)
    parser.add_argument("--load-model", type=str, default=None)

    parser.set_defaults(eval_on_train=None, eval_on_val=None, logger=True,
                        pin_memory=None, round_targets=False,
                        log_gradients=None)
    args = parser.parse_args()

    with open(args.config, 'r') as stream:
        config_dict = yaml.safe_load(stream)

    if torch.cuda.is_available() and (args.devices[0] != -1):
        # torch.backends.cudnn.deterministic = True
        torch.cuda.set_device(args.devices[0])

    modelCls = registry.lookup('model', config_dict['model'])
    model_preproc = registry.instantiate(
        modelCls.Preproc,
        config_dict['model']['preproc'])
    model_preproc.load()

    if args.logger:
        if args.logdir is None:
            raise ValueError("logdir cannot be null if logging is enabled")
        logger = TBLogger(args.logdir)
    else:
        logger = NoOpLogger()

    train_config = registry.construct(
        'train_config',
        merge_config_and_args(config_dict['train']['config'], args)
    )
    # Construct trainer and do training
    trainer: BaseTrainer = registry.construct(
        'trainer',
        config={'name' : config_dict['train']['name']},
        config_dict=config_dict,
        train_config=train_config,
        model_preproc=model_preproc,
        logger=logger)
    trainer.train(modeldir=args.logdir)


if __name__ == "__main__":
    main()
