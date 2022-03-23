from typing import Callable, Optional, Tuple

import torch

DatasetSplitFn = Callable[[torch.Dataset, torch.tenosr],
                          Tuple[torch.Datasest, torch.Dataset]]


def build_dataset_split(recon_epochs_max: int = 1,
                        recon_epochs_constant: bool = True,
                        recon_steps_max: Optional[int] = None,
                        post_recon_epochs: int = 1,
                        post_recon_steps_max: Optional[int] = None,
                        split_dataset: bool = False) -> DatasetSplitFn:

    def recon_condition(i, entry): return torch.tensor(
        i) % torch.tensor(2) == 0
    def post_recon_condition(i, entry): return torch.tensor(
        i) % torch.tensor(2) > 0

    def get_entry(i, entry): return entry

    def dataset_split(clinet_dataset, round_num: torch.Tensor):
        if split_dataset:
            recon_dataset = clinet_dataset.enumerate().filter(
                recon_condition).map(get_entry)
            post_recon_dataset = clinet_dataset.enumerate().filter(
                post_recon_condition).map(get_entry)

        else:
            recon_dataset = clinet_dataset
            post_recon_dataset = clinet_dataset

        # Number of reconstruction epochs is exactly recon_epochs_max if
        # recon_epochs_constant is True, and min(round_num, recon_epochs_max)
        # if not
        num_recon_epochs = recon_epochs_max
        if not recon_epochs_constant:
            num_recon_epochs = torch.minimum(round_num, recon_epochs_max)

        # Apply `num_recon_epochs`` before limiting to a maximum number of
        # batches if needed.
        recon_dataset = recon_dataset.repeat(num_recon_epochs)
        if recon_steps_max is not None:
            recon_dataset = recon_dataset.take(recon_steps_max)

        # Do the same for post-reconstruction.
        post_recon_dataset = post_recon_dataset.repeat(post_recon_epochs)
        if post_recon_steps_max is not None:
            post_recon_dataset = post_recon_dataset.take(post_recon_steps_max)

        return recon_dataset, post_recon_dataset
    return dataset_split
