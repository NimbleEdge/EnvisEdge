from typing import Dict

import attr
import numpy as np
import torch
from fedrec.user_modules.envis_base_module import EnvisBase
from fedrec.user_modules.envis_preprocessor import EnvisPreProcessor
from fedrec.utilities import registry
from fedrec.utilities import saver_utils as saver_mod
from sklearn import metrics
from tqdm import tqdm
from fedrec.utilities.logger import BaseLogger


@attr.s
class TrainConfig:
    """
    Class for Training config
    attrs gives class decorator and a way to
    define the attributes on class
    eval_every_n evaluates after every n epochs
    report_every_n reports after every n epochs
    save_every_n saves model after n epochs
    keep_every_n keeps it after n epochs
    """
    eval_every_n = attr.ib(default=10000)
    report_every_n = attr.ib(default=10)
    save_every_n = attr.ib(default=2000)
    keep_every_n = attr.ib(default=10000)

    batch_size = attr.ib(default=32)
    eval_batch_size = attr.ib(default=128)
    num_epochs = attr.ib(default=-1)

    num_batches = attr.ib(default=-1)

    @num_batches.validator
    def check_only_one_declaration(instance, _, value):
        """It checks so that there's only one declaration and raises value error if not

            Argument
            ---------
                instance:its an attribute whose object(num_epochs) is checked
                value:(int)


            Raises
            ------
            ValueError
                only one out of num_epochs and num_batches must be declared!
            """
        if instance.num_epochs > 0 & value > 0:
            raise ValueError(
                "only one out of num_epochs and num_batches must be declared!")

    num_eval_batches = attr.ib(default=-1)
    eval_on_train = attr.ib(default=False)
    eval_on_val = attr.ib(default=True)

    num_workers = attr.ib(default=0)
    pin_memory = attr.ib(default=True)
    log_gradients = attr.ib(default=False)


class EnvisTrainer(EnvisBase):
    """This class is to train Envis
    Arguments
    ------
    EnvisBase-we are using the envis base as the input parameter
    """
    def __init__(
            self,
            config_dict: Dict,
            logger: BaseLogger,
            client_id=None) -> None:
        """
        Initialize the EnvisTrainer class,it's run once when
        instantiating the Dataset object
        The super call delegates the function call to the
        parent class.This is needed to initialize properly.
        "register" means act of recording a name or information
        on an official list",model.cuda() adds support CUDA
        tensor types that implement the same function as
        CPU tensors.Returns the random number generator
        state as a torch.ByteTensor

        Argument
        ------
        dataset_config-It configures the dataset.
        logger-Base logger handler.
        client_id-(int) It's just an id.
         """
        super().__init__(config_dict)
        self.config_dict = config_dict
        self.client_id = client_id
        self.train_config = TrainConfig(**config_dict["trainer"]["config"])
        self.logger = logger
        modelCls = registry.lookup('model', config_dict["model"])
        self.model_preproc: EnvisPreProcessor = registry.instantiate(
            modelCls.Preproc,
            config_dict["model"]['preproc'], unused_keys=(),
            client_id=client_id)

        with self.model_random:
            # 1. Construct model
            self.model_preproc.load_data_description()
            self.model = registry.construct(
                'model', self.config_dict["model"],
                preprocessor=self.model_preproc,
                unused_keys=('name', 'preproc')
            )
            if torch.cuda.is_available():
                self.model.cuda()

        self._data_loaders = {}
        self._scheduler = None

        with self.init_random:
            self.optimizer = registry.construct(
                'optimizer', self.config_dict['trainer']['optimizer'],
                params=self.model.parameters())
        self._saver = None

    def reset_loaders(self):
        """Its used for reseting random loaders"""
        self._data_loaders = {}

    @staticmethod
    def _yield_batches_from_epochs(loader, start_epoch):
        """It's used to yield batches from epoch the batch
        size is a number of samples processed before the
        model is updated,epochs is the number of complete
        passes through the training dataset,The size of
        a batch must be more than or equal to one and
        less than or equal to the number
        of samples in the training dataset.

        Arguments
        --------
        loader-It's used to load the dataset.
        start_epoch-It's the starting epoch.

        Yields
        ------
        int
            batch, current_epoch
        """
        current_epoch = start_epoch
        while True:
            for batch in loader:
                yield batch, current_epoch
            current_epoch += 1

    def get_scheduler(self, optimizer, **kwargs):
        """It will init the scheduler based on the configuration provided to it.
        get_scheduler will change the learning rate based on  model
        optimizer implements various optimization algorithms.
        config_dict-python dict has associated pretrained model configurations as values.

            Arguments
            --------
            optimizer-It optimizes Model Parameters.
            **kwargs-Arbitrary keyword arguments.


            Returns
            --------
            self._scheduler

            """
        if self._scheduler is None:
            with self.init_random:
                self._scheduler = registry.construct(
                    'lr_scheduler',
                    self.config_dict['trainer'].get(
                        'lr_scheduler', {'name': 'noop'}),
                    optimizer=optimizer, **kwargs)
        return self._scheduler

    @property
    def saver(self):
        """ It's used for save the model paarmeters
        Returns
        --------
        self._saver-: Saves a serialized object to disk.
        """
        if self._saver is None:
            # 2. Restore model parameters
            self._saver = saver_mod.Saver(
                self.model, self.optimizer,
                keep_every_n=self.train_config.keep_every_n)
        return self._saver

    @property
    def data_loaders(self):
        """
        It's used for save the model paarmeters

        Returns
        -------
        data_loaders-that allow you to use pre-loaded
        datasets as well your own dataCombines a dataset
        and a sampler and provides an iterable over the
        given dataset,supports both map-style and
        iterable-style datasets with single- or multi-process
        loading, customizing loading order and optional
        automatic batching (collation) and memory pinning.
        """
        if self._data_loaders:
            return self._data_loaders
        # TODO : FIX if not client_id will load whole dataset
        self.model_preproc.load()
        # 3. Get training data somewhere
        with self.data_random:
            train_data = self.model_preproc.dataset('train')
            train_data_loader = self.model_preproc.data_loader(
                train_data,
                batch_size=self.train_config.batch_size,
                num_workers=self.train_config.num_workers,
                pin_memory=self.train_config.pin_memory,
                persistent_workers=True,
                shuffle=True,
                drop_last=True)

        train_eval_data_loader = self.model_preproc.data_loader(
            train_data,
            pin_memory=self.train_config.pin_memory,
            num_workers=self.train_config.num_workers,
            persistent_workers=True,
            batch_size=self.train_config.eval_batch_size)

        val_data = self.model_preproc.dataset('val')
        val_data_loader = self.model_preproc.data_loader(
            val_data,
            num_workers=self.train_config.num_workers,
            pin_memory=self.train_config.pin_memory,
            persistent_workers=True,
            batch_size=self.train_config.eval_batch_size)
        self._data_loaders = {
            'train': train_data_loader,
            'train_eval': train_eval_data_loader,
            'val': val_data_loader
        }

    @staticmethod
    def eval_model(
            model,
            loader,
            eval_section,
            logger,
            num_eval_batches=-1,
            best_acc_test=None,
            best_auc_test=None,
            step=-1):
        """
        It's the evaluation model .
        The scores and the targets would be stored in  a list.
        We do 3 tests here S test ,Z test and T test append
        S_test.Then we calculate the recall,precision average
        precision score,f1 score  roc _ auc and
        finally the accuracy.

        Arguments
        ----------
        model-It loads the model.
        loader-It helps to load the model.
        eval_section-Its the evauation section.
        logger-the use loggers is to just pass a list to the Traine.
        num_eval_batches(int)-It gives us the no of evaluation batches
        best_acc_test-It gives us the best accuracy
        best_auc_test-It provides thae best ggregate measure of
        performance across all possible classification threshold.
        step-(int) It counts the no of steps.

        Returns
        -------
        bool-true
        if best_auc_test is not None else returns false
        results-(dict)
        """
        scores = []
        targets = []
        model.eval()
        total_len = num_eval_batches if num_eval_batches > 0 else len(loader)
        with torch.no_grad():
            t_loader = tqdm(enumerate(loader), unit="batch", total=total_len)
            for i, testBatch in t_loader:
                # early exit if nbatches was set by the user and was exceeded
                if (num_eval_batches > 0) and (i >= num_eval_batches):
                    break
                t_loader.set_description(f"Running {eval_section}")

                inputs, true_labels = testBatch

                # forward pass
                Z_test = model.get_scores(model(inputs))

                S_test = Z_test.detach().cpu().numpy()  # numpy array
                T_test = true_labels.detach().cpu().numpy()  # numpy array

                scores.append(S_test)
                targets.append(T_test)

        model.train()
        scores = np.concatenate(scores, axis=0)
        targets = np.concatenate(targets, axis=0)
        metrics_dict = {
            "recall": lambda y_true, y_score: metrics.recall_score(
                y_true=y_true, y_pred=np.round(y_score)
            ),
            "precision": lambda y_true, y_score: metrics.precision_score(
                y_true=y_true, y_pred=np.round(y_score), zero_division=0.0
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

        results = {}
        for metric_name, metric_function in metrics_dict.items():
            results[metric_name] = metric_function(targets, scores)
            logger.add_scalar(
                eval_section + "/" + "mlperf-metrics/" + metric_name,
                results[metric_name],
                step,
            )

        if (best_auc_test is not None) and\
                (results["roc_auc"] > best_auc_test):
            best_auc_test = results["roc_auc"]
            best_acc_test = results["accuracy"]
            return True, results

        return False, results

    def store_state(self):
        """
        It's the store state which
        stores the model and retuns it.
        Returns
        --------
        model-Returns the state of the model.
        """
        assert self.model is not None
        return {
            'model': self.model
        }

    def test(self):
        """
        It gives us the results on the test data computes
        with respect to training dataset and the validation data
        taking the parameters data loaders,num_eval_batches
        and logger function with the intitial step value-=1
        and finally returns test results

        Returns
        ---------
        results(dict)-the test results are returned
        """
        results = {}
        if self.train_config.eval_on_train:
            _, results['train_metrics'] = self.eval_model(
                self.model,
                self.data_loaders['train_eval'],
                eval_section='train_eval',
                num_eval_batches=self.train_config.num_eval_batches,
                logger=self.logger, step=-1)

        if self.train_config.eval_on_val:
            _, results['test_metrics'] = self.eval_model(
                self.model,
                self.data_loaders['test'],
                eval_section='test',
                logger=self.logger,
                num_eval_batches=self.train_config.num_eval_batches,
                step=-1)
        return results

    def train(self, modeldir=None):
        """
        It gives us the results on the train dataset
        lr_scheduler here is the learning rate scheduler
        which  detemines the step size at each parameter
        and optimizes,calculates the total training length
        loading the training parameters ,training the model,
        tqdm is the default iterator, it takes an iterator object
        as argument,and displays a progress bar as
        it iterates over it applying the gradient
        and then computing the metrics such as training
        loss saving the model and then returning it.

        Arguments
        ------------
        modeldir-the model.

        Returns(dict) the trained model.
        ---------
        results(dict)
        """
        last_step, current_epoch = self.saver.restore(modeldir)
        lr_scheduler = self.get_scheduler(
            self.optimizer, last_epoch=last_step)

        if self.train_config.num_batches > 0:
            total_train_len = self.train_config.num_batches
        else:
            total_train_len = len(self.data_loaders['train'])
        train_dl = self._yield_batches_from_epochs(
            self.data_loaders['train'], start_epoch=current_epoch)

        # 4. Start training loop
        with self.data_random:
            best_acc_test = 0
            best_auc_test = 0
            dummy_input = next(iter(train_dl))[0]
            self.logger.add_graph(self.model, dummy_input[0])
            t_loader = tqdm(train_dl, unit='batch',
                            total=total_train_len)
            for batch, current_epoch in t_loader:
                t_loader.set_description(f"Training Epoch {current_epoch}")

                # Quit if too long
                if self.train_config.num_batches > 0 and\
                        last_step >= self.train_config.num_batches:
                    break
                if self.train_config.num_epochs > 0 and\
                        current_epoch >= self.train_config.num_epochs:
                    break

                # Evaluate model
                if last_step % self.train_config.eval_every_n == 0:
                    if self.train_config.eval_on_train:
                        self.eval_model(
                            self.model,
                            self.data_loaders['train_eval'],
                            'train_eval',
                            self.logger,
                            self.train_config.num_eval_batches,
                            step=last_step)

                    if self.train_config.eval_on_val:
                        if self.eval_model(
                                self.model,
                                self.data_loaders['val'],
                                'val',
                                self.logger,
                                self.train_config.num_eval_batches,
                                best_acc_test=best_acc_test,
                            best_auc_test=best_auc_test,
                                step=last_step)[1]:
                            self.saver.save(modeldir, last_step,
                                            current_epoch, is_best=True)

                # Compute and apply gradient
                with self.model_random:
                    input, true_label = batch
                    output = self.model(input)
                    loss = self.model.loss(output, true_label)
                    self.optimizer.zero_grad()
                    loss.backward()
                    self.optimizer.step()
                    lr_scheduler.step()

                # Report metrics
                if last_step % self.train_config.report_every_n == 0:
                    t_loader.set_postfix({'loss': loss.item()})
                    self.logger.add_scalar(
                        'train/loss', loss.item(), global_step=last_step)
                    self.logger.add_scalar(
                        'train/lr',  lr_scheduler.last_lr[0],
                        global_step=last_step)
                    if self.train_config.log_gradients:
                        self.logger.log_gradients(self.model, last_step)

                last_step += 1
                # Run saver
                if last_step % self.train_config.save_every_n == 0:
                    self.saver.save(modeldir, last_step, current_epoch)
        return self.model.state_dict()

    def update(self, state: Dict):
        # Update the model
        """PyTorch Tensor can run on either CPU or GPU,that's why we are
            returning the model in tensor
        """
        self.model.load_state_dict(state["model"].tensors)
        # # Update the optimizer
        # self.optimizer.load_state_dict(state["optimizer"].tensors)
        # # empty dataloaders for new dataset
        # self.reset_loaders()
        # # update dataset
        # self.model_preproc = state["model_preproc"]
