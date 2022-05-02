import os
import os.path
from typing import Tuple

import pandas as pd
from datasets.femnist.femnist_dataset import FemnistDataset
from fedrec.utilities import registry


@registry.load("dataset", "femnist")
class FemnistProcessor:

    def __init__(
            self,
            data_dir,
            splits,
            normalize=((0.1307,), (0.3081,))):
        self.data_dir = data_dir
        self.meta_data_dir = os.path.join(data_dir, 'client_data_mapping')
        self.splits = splits
        self.img_urls = {split: None for split in splits}
        self.labels = {split: None for split in splits}
        self.normalize = normalize

    def process_data(self):
        '''This method performs data transformations and splits the data'''
        for split in self.splits:
            print(f"preprocessing data_{split}...")
            _, df = self.process_file(split)
            self.create_index_file(split, df)

    def process_file(self, split) -> Tuple[str, pd.DataFrame]:
        '''This method reads a csv file into a dataframe and then sorts the dataframe values'''
        print("preprocessing datasset...")
        output_path = self.meta_data_dir+"/{}_processed.csv".format(split)
        if os.path.exists(output_path):
            return output_path, None
        df = pd.read_csv(self.meta_data_dir + f"/{split}.csv")
        self.sort_values(df)
        df.to_csv(output_path)
        return output_path, df

    def sort_values(self, df: pd.DataFrame):
        '''Using this method, values are sorted by client_id, and then reset by reset_index. The index column is then dropped off'''
        print("Sorting values...")
        df.sort_values(by=["client_id"], inplace=True)
        df.reset_index(inplace=True)
        df.drop(columns=["index"], inplace=True)

    def create_index_file(self, split, df: pd.DataFrame = None):
        '''This method creates an index file with columns client_id,startindex,lastindex and converts it into a CSV file'''
        print("Creating index file...")
        data = []
        file_path = self.meta_data_dir + f"/{split}_processed.csv"
        if df is None:
            df = df.read_csv(file_path)

        for id in df.client_id.unique():
            tmp = df[df["client_id"] == id]
            startindex = tmp.first_valid_index()
            lastindex = tmp.last_valid_index()
            data.append([id, startindex, lastindex])
        df_index = pd.DataFrame(data,
                                columns=['client_id',
                                         'startindex', 'lastindex']
                                )
        df_index.to_csv(self.meta_data_dir+f"/{split}_index.csv", index=True)

    def load_meta_data(self, split, start_offset, num_samples):
        '''This method loads meta data of csv file and returns the list values of sample_path and label_id'''
        df_values = pd.read_csv(
            self.meta_data_dir + f"/{split}_processed.csv",
            names=["index", "client_id", "sample_path",
                   "label_name", "label_id"],
            skiprows=start_offset,
            nrows=num_samples,
            delimiter=",",
        )
        df_values = df_values.drop(labels=0, axis=0)
        return (
            df_values.sample_path.to_list(),
            df_values.label_id.to_list()
        )

    def load(self, client_id=None):
        ''' if client_id cannot be located, this method raises an error; otherwise, it reads the csv file and loads the metadata to determine labels'''
        if client_id is None:
            raise NotImplementedError
        for split in self.splits:
            df_index = pd.read_csv(self.meta_data_dir + f"/{split}_index.csv")
            start_idx = df_index.iloc[client_id]["startindex"]
            end_idx = df_index.iloc[client_id]["lastindex"]
            # load meta file to get labels
            self.img_urls[split], self.labels[split] = self.load_meta_data(
                split, start_idx, end_idx)

    def dataset(self, split):
        '''This method returns Femnist Dataset'''
        return FemnistDataset(
            data_dir=self.data_dir,
            img_urls=self.img_urls[split],
            targets=self.labels[split],
            normalize=((self.normalize[0],), (self.normalize[1],)))
