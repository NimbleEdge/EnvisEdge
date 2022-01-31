from argparse import ArgumentParser

import numpy as np
import torch
import yaml
from sklearn import metrics

from fedrec.utilities import random_state, registry
from fedrec.utilities.serialization import dash_separated_floats


class InferenceMaker:
    """
    Tests our model on the testing dataset (test-loader)
    """

    def __init__(self, config, devices, log_dir) -> None:
        """The __init__ method lets the class
        initialize the objects attributes

        Arguments:
        ---
            config (yml file): file with the parameter values for training.
            devices (list): list of available devices
            log_dir (string): directory of the logs from the experiment
        """
        self.devices = devices
        if torch.cuda.is_available():
            torch.backends.cudnn.deterministic = True
            device = torch.device("cuda", 0)
        else:
            device = torch.device("cpu")
            print("Using CPU...")
        self.log_dir = log_dir
        self.train_config = config
        self.data_random = random_state.RandomContext(
            config.get("data_seed", None))
        self.model_random = random_state.RandomContext(
            config.get("model_seed", None))
        self.init_random = random_state.RandomContext(
            config.get("init_seed", None))
        with self.init_random:
            self.preproc = registry.construct(
                'preproc', config['model']['preproc'])
            self.synthesizer = registry.construct()
            self.optimizer = registry.construct(
                'optimizer', config['train'])
        self.lr_scheduler = registry.construct(
            'lr_scheduler', config['train'])

        with self.model_random:
            # 1. Construct model
            modelCls = registry.lookup('model', config['model'])
            self.model_preproc = registry.instantiate(
                modelCls.Preproc,
                config['model'],
                unused_keys=('name',))
            self.model_preproc.load()

            self.model = registry.instantiate(
                modelCls, config['model'],
                unused_keys=(), device=device
            )

        if torch.cuda.is_available():
            # Custom Model-Data Parallel
            # the mlps are replicated and use data parallelism, while
            # the embeddings are distributed and use model parallelism
            self.model = self.model.cuda()

    def inference(
        self,
        model,
        test_loader
    ):
        """
            Makes an inference from the model by testing it against
            the testing dataset and calculates the metrics on it.
        Arguments:
        ---
            model (pytorch.model): the model variable
            test_loader (Dataloader): Testing dataset

        Returns:
        ---
            list of dict: dictionary contains the metrics used for test,
            namely (recall, precision, f1-score, average-precision-score,
            roc_auc-score and accuracy)
        """
        test_accu = 0
        test_samp = 0
        scores = []
        targets = []
        model.eval()
        for i, testBatch in enumerate(test_loader):
            inputs, true_labels = testBatch

            # forward pass
            Z_test = model(*inputs)

            S_test = Z_test.detach().cpu().numpy()  # numpy array
            T_test = true_labels.detach().cpu().numpy()  # numpy array

            mbs_test = T_test.shape[0]  # = mini_batch_size except last
            A_test = np.sum((np.round(S_test, 0) == T_test).astype(np.uint8))

            test_accu += A_test
            test_samp += mbs_test
        scores = np.concatenate(scores, axis=0)
        targets = np.concatenate(targets, axis=0)

        metrics_dict = {
            "recall": lambda y_true, y_score: metrics.recall_score(
                y_true=y_true, y_pred=np.round(y_score)
            ),
            "precision": lambda y_true, y_score: metrics.precision_score(
                y_true=y_true, y_pred=np.round(y_score)
            ),
            "f1": lambda y_true, y_score: metrics.f1_score(
                y_true=y_true, y_pred=np.round(y_score)
            ),
            "ap": metrics.average_precision_score,
            "roc_auc": metrics.roc_auc_score,
            "accuracy": lambda y_true, y_score: metrics.accuracy_score(
                y_true=y_true, y_pred=np.round(y_score)
            ),
        }

        return {
            metric_name: metric_function(targets, scores)
            for metric_name, metric_function in metrics_dict.items()
        }


def main():
    """
        Parses the arguments passed in the command
        line and creates a tester and tests the model.

    """
    parser = ArgumentParser()
    parser.add_argument("--weighted-pooling", type=str, default=None)
    # activations and loss
    parser.add_argument("--loss-function", type=str,
                        default="mse")  # or bce or wbce
    parser.add_argument(
        "--loss-weights", type=dash_separated_floats, default="1.0-1.0"
    )  # for wbce
    parser.add_argument("--loss-threshold", type=float,
                        default=0.0)  # 1.0e-7
    parser.add_argument("--round-targets", type=bool, default=False)
    # data
    parser.add_argument("--data-size", type=int, default=1)
    parser.add_argument("--num-batches", type=int, default=0)
    parser.add_argument(
        "--data-generation", type=str, default="random"
    )  # synthetic or dataset

    parser.add_argument(
        "--dataset-multiprocessing",
        action="store_true",
        default=False,
        help="The Kaggle dataset can be multiprocessed in an environment \
            with more than 7 CPU cores and more than 20 GB of memory. \n \
            The Terabyte dataset can be multiprocessed in an environment \
            with more than 24 CPU cores and at least 1 TB of memory.",
    )
    # gpu
    parser.add_argument("--use-gpu", action="store_true", default=False)
    # store/load model
    parser.add_argument("--save-model", type=str, default="")
    parser.add_argument("--load-model", type=str, default="")
    args = parser.parse_args()

    with open(args.config, 'r') as stream:
        config = yaml.safe_load(stream)

    # Construct tester and do testing
    tester = InferenceMaker(logger, config)
    tester.inference(config, modeldir=args.logdir)


if __name__ == "__main__":
    main()
