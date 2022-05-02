import os
import os.path
from torchvision import transforms

import torch
from PIL import Image


class FemnistDataset(torch.utils.data.Dataset):
    """
    Args:
        root (string): Root directory of dataset where
        ``MNIST/processed/training.pt`` and
            ``MNIST/processed/test.pt`` exist.
        train (bool, optional): If True, creates dataset from ``training.pt``,
            otherwise from ``test.pt``.
        download (bool, optional): If true, downloads the dataset
        from the internet and puts it in root directory. If dataset is
        already downloaded, it is not downloaded again.
        transform (callable, optional): A function/transform that  takes in
        an PIL image and returns a transformed version.
            E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that
        takes in the target and transforms it.
    """

    def __init__(
            self,
            data_dir,
            img_urls,
            targets,
            normalize=((0.1307,), (0.3081,))
    ):

        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(*normalize)
        ])
        self.data_dir = data_dir
        self.img_urls = img_urls
        self.targets = targets

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is index of the target class.
        """
        imgName, target = self.img_urls[index], int(self.targets[index])
        # doing this so that it is consistent with all other datasets
        # to return a PIL Image
        img = Image.open(os.path.join(self.data_dir, imgName))
        # avoid channel error
        if img.mode != 'RGB':
            img = img.convert('RGB')
        # apply transform over the image
        if self.transform is not None:
            img = self.transform(img)
        return img, target

    def __len__(self):
        return len(self.img_urls)
