
from argparse import ArgumentParser
from fedrec.utilities import random_state, registry
import fl_strategies
import experiments
import yaml


class Processor:
    def __init__(self, config, log_dir) -> None:
        self.log_dir = log_dir
        self.model_random = random_state.RandomContext(
            config.get("model_seed", None))

        with self.model_random:
            # 1. Construct model
            modelCls = registry.lookup('model', config['model'])
            self.model_preproc = registry.instantiate(
                modelCls.Preproc,
                config['model']['preproc'])

    def process(self):
        self.model_preproc.preprocess_data()


def main():
    parser = ArgumentParser()
    parser.add_argument("--config", type=str)
    parser.add_argument("--logdir", type=str)

    parser.add_argument(
        "--dataset-multiprocessing",
        action="store_true",
        default=True,
        help="The Kaggle dataset can be multiprocessed in an environment \
                with more than 7 CPU cores and more than 20 GB of memory. \n \
                The Terabyte dataset can be multiprocessed in an environment \
                with more than 24 CPU cores and at least 1 TB of memory.",
    )
    # gpu
    parser.add_argument("--use-gpu", action="store_true", default=False)

    args = parser.parse_args()

    with open(args.config, 'r') as stream:
        config = yaml.safe_load(stream)

    Processor(config, args.logdir).process()


if __name__ == "__main__":
    main()
