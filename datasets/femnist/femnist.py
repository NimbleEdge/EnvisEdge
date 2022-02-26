"""
Fan Lai and Yinwei Dai and Xiangfeng Zhu and Harsha V. Madhyastha and Mosharaf
Chowdhury (2021) FedScale: Benchmarking Model and System Performance of
Federated Learning at Scale [code]. "www.fedscale.ai".
"""
import csv
import os
import os.path

import pandas as pd
from PIL import Image


class FEMNIST():
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
            client_id,
            data_dir,
            split: str = 'train',
            transform=None,
            target_transform=None):

        self.split = split  # 'train', 'test', 'validation'
        # client_id for sending message to trainer
        self.client_id = client_id
        self.transform = transform
        self.target_transform = target_transform
        self.data_path = os.path.join(data_dir, self.split+".csv")
        # load data and targets
        self.data, self.targets = self.load_file(self.data_path)

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is index of the target class.
        """

        imgName, target = self.data[index], int(self.targets[index])

        # doing this so that it is consistent with all other datasets
        # to return a PIL Image
        img = Image.open(os.path.join(self.root, imgName))

        # avoid channel error
        if img.mode != 'RGB':
            img = img.convert('RGB')

        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target

    def __len__(self):
        return len(self.data)

    @property
    def raw_folder(self):
        return self.root

    @property
    def processed_folder(self):
        return self.root

    def _check_exists(self):
        return (os.path.exists(os.path.join(self.processed_folder,
                                            self.split)))

    def load_meta_data(self, path):
        datas, labels = [], []

        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count != 0:
                    datas.append(row[1])
                    labels.append(int(row[-1]))
                line_count += 1

        return datas, labels

    def load_file(self, path):

        # load meta file to get labels
        datas, labels = self.load_meta_data(os.path.join(
            self.processed_folder, 'client_data_mapping',
            self.split+'.csv'))

        return datas, labels

    def get_index_data(path, output_path):
        data = []
        df = pd.read_csv(path)
        df.sort_values(by=["client_id"], inplace=True)
        df.reset_index(inplace=True)
        df.drop(columns=["index"], inplace=True)
        for id in df.client_id.unique():
            tmp = df[df["client_id"] == id]
            startindex = tmp.first_valid_index()
            lastindex = tmp.last_valid_index()
            data.append([id, startindex, lastindex])
        df_index = pd.DataFrame(data,
                                columns=['client_id',
                                         'startindex', 'lastindex']
                                )
        df_index.to_csv(output_path+"/index.csv", index=False)
