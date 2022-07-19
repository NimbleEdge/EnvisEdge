import sys

from fedrec.utilities import registry
from torch.optim.lr_scheduler import _LRScheduler


@registry.load('lr_scheduler', 'dlrm')
class LRPolicyScheduler(_LRScheduler):
    """
    This class is used to adjust the learning rate of the optimizer during
    training. It implements the LRPolicy, which is a learning rate decay
    policy as described in the paper "`Demystifying Learning Rate Policies
    for High Accuracy Training of Deep Neural Networks
    <https://arxiv.org/pdf/1908.06477.pdf>`_".
    
    The LRPolicy is designed to decrease the learning rate after a fixed
    number of epochs, and increase it after a fixed number of epochs. The
    LRScheduler is a wrapper around the Pytorch LRScheduler class, and is
    used to adjust the learning rate of the optimizer.

    Arguments:
        optimizer():
            Optimizer instance. This is the optimizer that will be used to
            update the model.
        num_warmup_steps():
            Number of warmup steps. The learning rate will be increased after
            this number of steps.
        decay_start_step():
            Step at which the learning rate decay starts. The learning rate
            will be decreased after this number of steps.
        num_decay_steps():
            Number of steps after which the learning rate will be decreased.
        
    Method:
        get_lr():
            Returns the learning rate for the current step. This method is
            called by the optimizer to get the learning rate for the current
            step.
    """
    def __init__(self,
                 optimizer,
                 num_warmup_steps,
                 decay_start_step,
                 num_decay_steps):
        self.num_warmup_steps = num_warmup_steps
        self.decay_start_step = decay_start_step
        self.decay_end_step = decay_start_step + num_decay_steps
        self.num_decay_steps = num_decay_steps

        if self.decay_start_step < self.num_warmup_steps:
            sys.exit(
                "Learning rate warmup must finish before the decay starts")

        super(LRPolicyScheduler, self).__init__(optimizer)

    def get_lr(self):
        step_count = self._step_count
        if step_count < self.num_warmup_steps:
            # warmup
            scale = 1.0 - (self.num_warmup_steps - step_count) / \
                self.num_warmup_steps
            lr = [base_lr * scale for base_lr in self.base_lrs]
            self.last_lr = lr
        elif self.decay_start_step <= step_count and \
                step_count < self.decay_end_step:
            # decay
            decayed_steps = step_count - self.decay_start_step
            scale = ((self.num_decay_steps - decayed_steps) /
                     self.num_decay_steps) ** 2
            min_lr = 0.0000001
            lr = [max(min_lr, base_lr * scale) for base_lr in self.base_lrs]
            self.last_lr = lr
        else:
            if self.num_decay_steps > 0:
                # freeze at last, either because we're after decay
                # or because we're between warmup and decay
                lr = self.last_lr
            else:
                # do not adjust
                lr = self.base_lrs
        return lr
