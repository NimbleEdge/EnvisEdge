"""Tools to save/restore model from checkpoints."""

import shutil
import os
import re

import torch

CHECKPOINT_PATTERN = re.compile('^model_checkpoint-(\d+)$')


class ArgsDict(dict):
    """
    The ArgsDict class creates dictionaries from its input arguments. It
    is used to create a dictionary of arguments for the model, trainer, etc.
    from a configuration file. The dictionary is then used to initialize the
    model, trainer, etc.
    
    The dictionary is created from the input arguments in the order they are
    passed to the function. The dictionary is then converted to a dictionary
    of arguments for the model, trainer, etc. by using the __dict__ attribute
    of the ArgsDict class. This is done to avoid the use of the __dict__
    attribute of the dictionary class.

    Argument
    ----------
    **kwargs:
        Variable keyword arguments for the ArgsDict class.
    """

    def __init__(self, **kwargs):
        super(ArgsDict, self).__init__()
        for key, value in kwargs.items():
            self[key] = value
        self.__dict__ = self


def create_link(original, link_name):
    """
    This function creates a symbolic link to the original file.
    If the link already exists, it deletes it and creates a new
    one. This is useful for keeping the latest checkpoint.
    """

    if os.path.islink(link_name):
        os.unlink(link_name)
    try:
        os.symlink(os.path.basename(original), link_name)
    except OSError:
        shutil.copy2(original, link_name)


def load_checkpoint(model,
                    optimizer,
                    model_dir,
                    map_location=None,
                    step=None):
    """
    This function loads the model and the optimizer checkpoints from the
    given model directory if it exists, and if the path to the model directory
    does not exist, it returns without errors.
    
    This is useful for loading the model from a checkpoint when the model
    directory does not exist. It also loads the current training step.

    Arguments
    ----------
    map_location: str, optional
        Location for the model and optimizer to be loaded from.
    step: int, optional
        Step to load the checkpoint from. If None, the latest checkpoint
        is loaded.
    """

    path = os.path.join(model_dir, 'model_checkpoint')
    if step is not None:
        path += '-{:08d}'.format(step)
    if os.path.exists(path):
        print("Loading model from %s" % path)
        checkpoint = torch.load(path, map_location=map_location)
        model.load_state_dict(checkpoint['model'], strict=False)
        optimizer.load_state_dict(checkpoint['optimizer'])
        return checkpoint.get('step', 0), checkpoint.get('epoch', 0)
    return 0, 0


def load_and_map_checkpoint(model, model_dir, remap):
    """
    This function loads the model and the optimizer checkpoints from the
    given model directory, then maps the state dictionaries.
    
    It filters out unnecessary keys from state_dict, overwrites entries
    in the existing state_dict, and maps the state_dict before loading
    the new state_dict.
    """

    path = os.path.join(model_dir, 'model_checkpoint')
    print("Loading parameters %s from %s" % (remap.keys(), model_dir))
    checkpoint = torch.load(path)
    new_state_dict = model.state_dict()
    for name, value in remap.items():
        # TODO: smarter mapping.
        new_state_dict[name] = checkpoint['model'][value]
    model.load_state_dict(new_state_dict)


def save_checkpoint(model,
                    optimizer,
                    step,
                    epoch,
                    model_dir,
                    is_best,
                    ignore=[],
                    keep_every_n=10000000):
    """
    This function saves the model and the optimizer checkpoints to the
    given model directory. It also saves the current training step and
    epoch, also creates a symbolic link to the latest checkpoint.

    Additionally, it stores all checkpoints for the traversal of these
    checkpoints, then deletes the oldest checkpoint if the number of
    checkpoints exceeds the keep_every_n. This is useful for keeping
    the latest checkpoint.
    """

    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    path_without_step = os.path.join(model_dir, 'model_checkpoint')
    step_padded = format(step, '08d')
    state_dict = model.state_dict()
    if ignore:
        for key in state_dict.keys():
            for item in ignore:
                if key.startswith(item):
                    state_dict.pop(key)
    path_with_step = '{}-{}'.format(path_without_step, step_padded)
    torch.save({
        'model': state_dict,
        'optimizer': optimizer.state_dict(),
        'epoch': epoch,
        'step': step
    }, path_with_step)
    create_link(path_with_step, path_without_step)
    create_link(path_with_step, os.path.join(model_dir, 'best_checkpoint'))

    # Cull old checkpoints.
    if keep_every_n is not None:
        all_checkpoints = []
        for name in os.listdir(model_dir):
            m = CHECKPOINT_PATTERN.match(name)
            if m is None or name == os.path.basename(path_with_step):
                continue
            checkpoint_step = int(m.group(1))
            all_checkpoints.append((checkpoint_step, name))
        all_checkpoints.sort()

        last_step = float('-inf')
        for checkpoint_step, name in all_checkpoints:
            if checkpoint_step - last_step >= keep_every_n:
                last_step = checkpoint_step
                continue
            os.unlink(os.path.join(model_dir, name))


class Saver(object):
    """
    This class manages save and restore for the model and optimizer
    checkpoints. It saves the model and optimizer checkpoints
    during training and loads the model and optimizer checkpoints
    during testing.
    
    It also manages the creation of the model and optimizer checkpoints
    for training, creates a directory for the model checkpoint,
    saves the checkpoints for model and optimizer, and also saves the
    current training step. Additionally, it creates a symbolic link to the
    latest checkpoint, and also to the best checkpoint.
    ...

    Arguments
    ----------
    model: Any
        The model checkpoint to be saved.
    optimizer: Any
        The optimizer checkpoint to be saved.
    keep_every_n: int, optional (default=10000000)
        The number of checkpoints to keep. If None, all checkpoints are kept.

    Attributes
    ----------
    _model: Any
        Stores the model checkpoint.
    _optimizer: Any
        Stores the optimizer checkpoint.
    _keep_every_n: int (default=10000000)
        Stores the upper bound value.

    Methods
    -------
    restore()
        This method restores the model and optimizer checkpoints from
        the given model directory.
    save()
        This method saves the model and optimizer checkpoints to the
        given model directory.
    restore_part()
        This method restores the model and optimizer checkpoints from
        the given model directory. Useful to initialize part of the model
        with another pretrained model.
    """

    def __init__(self, model, optimizer, keep_every_n=None):
        self._model = model
        self._optimizer = optimizer
        self._keep_every_n = keep_every_n

    def restore(self, model_dir=None, map_location=None, step=None):
        if model_dir is None:
            return 0, 0
        last_step, epoch = load_checkpoint(
            self._model, self._optimizer, model_dir, map_location, step)
        return last_step, epoch

    def save(self, model_dir, step, epoch, is_best=False):
        if model_dir is None:
            return
        save_checkpoint(self._model, self._optimizer, step, epoch, model_dir,
                        keep_every_n=self._keep_every_n, is_best=is_best)

    def restore_part(self, other_model_dir, remap):
        load_and_map_checkpoint(self._model, other_model_dir, remap)
