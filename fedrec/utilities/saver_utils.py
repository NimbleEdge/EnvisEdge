"""Tools to save/restore model from checkpoints."""

import shutil
import os
import re

import torch

CHECKPOINT_PATTERN = re.compile('^model_checkpoint-(\d+)$')


class ArgsDict(dict):
    """
    The ArgsDict class creates dictionaries from its input arguments.
    ...
    Argument
    ----------
    **kwargs:
        variable keyword arguments for the ArgsDict class.

    """

    def __init__(self, **kwargs):
        super(ArgsDict, self).__init__()
        for key, value in kwargs.items():
            self[key] = value
        self.__dict__ = self


def create_link(original, link_name):
    """This function links two paths symbolically if there is no link
    already."""
    
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
    """This function loads the model and the optimizer checkpoints from the
    given model directory if it exists, and if the path to the model
    directory does not exist, it returns without errors."""

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
    """This function loads the model and the optimizer checkpoints, then
    maps the state dictionaries."""

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
    """This function creates a directory for the model checkpoint, saves the
    checkpoints for model and optimizer, and also saves the current training
    step.
    
    It stores all checkpoints for the traversal of these checkpoints, then
    deletes the file path at each checkpoint."""

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
    checkpoints.

    ...

    Arguments
    ----------
    model: Any
        model checkpoint to be saved.
    optimizer: Any
        optimizer checkpoint to be saved.
    keep_every_n: optional
        upper bound value needed to get the highest checkpoint step.
        Default is None.

    Attributes
    ----------
    _model
        stores the model checkpoint.
    _optimizer
        stores the optimizer checkpoint.
    _keep_every_n
        stores the upper bound value.

    Methods
    -------
    restore()
        restores model and optimizer checkpoints from the given model
        directory.
    save()
        saves model and optimizer checkpoints to the given model directory.
    restore_part()
        stores part of the model from other model directory.
        Useful to initialize part of the model with another pretrained model.

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
