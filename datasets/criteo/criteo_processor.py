
import os
from collections import defaultdict

import numpy as np
from datasets.criteo.criteo_dataset import (CriteoDataset,
                                            collate_wrapper_criteo_length)
from fedrec.utilities import registry
from torch.multiprocessing import Manager, Process

# Kaggle Display Advertising Challenge Dataset
# dataset (str): name of dataset (Terabyte)
# randomize (str): determines randomization scheme
#            "none": no randomization
#            "day": randomizes each day"s data (only works if split = True)
#            "total": randomizes total dataset
# split (bool) : to split into train, test, validation data-sets


@registry.load('dataset', 'kaggle')
class CriteoDataProcessor:
    def __init__(
            self,
            datafile,
            output_file,
            max_ind_range=0,
            sub_sample_rate=0.0,
            randomize="day",
            dataset_multiprocessing=False,
    ):
        self.datafile = datafile
        self.output_file = output_file
        lstr = datafile.split("/")
        self.d_path = "/".join(lstr[0:-1]) + "/"
        self.d_file = lstr[-1].split(".")[0]
        self.npzfile = self.d_path + (self.d_file + "_day")
        self.trafile = self.d_path + (self.d_file + "_fea")
        self.total_file = self.d_path + self.d_file + "_day_count.npz"

        self.dataset_multiprocessing = dataset_multiprocessing
        self.sub_sample_rate = sub_sample_rate
        self.days = 7
        # dataset
        # tar_fea = 1   # single target
        self.den_fea = 13  # 13 dense  features
        # spa_fea = 26  # 26 sparse features
        # tad_fea = tar_fea + den_fea
        # tot_fea = tad_fea + spa_fea
        self.randomize = randomize
        self.max_ind_range = max_ind_range
        self.clear_items()

    @staticmethod
    def _process_one_file(
            datfile,
            npzfile,
            split,
            num_data_in_split,
            dataset_multiprocessing,
            days,
            sub_sample_rate=0.0,
            convertDictsDay=None,
            resultDay=None
    ):
        if dataset_multiprocessing:
            convertDicts_day = [{} for _ in range(26)]
        else:
            convertDicts = {}

        with open(str(datfile)) as f:
            y = np.zeros(num_data_in_split, dtype="i4")  # 4 byte int
            X_int = np.zeros((num_data_in_split, 13), dtype="i4")  # 4 byte int
            X_cat = np.zeros((num_data_in_split, 26), dtype="i4")  # 4 byte int
            if sub_sample_rate == 0.0:
                rand_u = 1.0
            else:
                rand_u = np.random.uniform(
                    low=0.0, high=1.0, size=num_data_in_split)

            i = 0
            percent = 0
            for k, line in enumerate(f):
                # process a line (data point)
                out = CriteoDataProcessor._transform_line(
                    line,
                    rand_u if sub_sample_rate == 0.0 else rand_u[k],
                    sub_sample_rate)
                if out is None:
                    continue
                y[i], X_int[i], X_cat[i] = out
                # count uniques
                if dataset_multiprocessing:
                    for j in range(26):
                        convertDicts_day[j][X_cat[i][j]] = 1
                    # debug prints
                    if float(i)/num_data_in_split*100 > percent+1:
                        percent = int(float(i)/num_data_in_split*100)
                        print(
                            "Load %d/%d (%d%%) Split: %d  Label True: %d"
                            % (i, num_data_in_split, percent, split, y[i],),
                            end="\n",
                        )
                else:
                    for j in range(26):
                        convertDicts[j][X_cat[i][j]] = 1
                    print(
                        "Load %d/%d  Split: %d  Label True: %d"
                        % (i, num_data_in_split, split, y[i],), end="\r",
                    )
                i += 1

            filename_s = npzfile + "_{0}.npz".format(split)
            if os.path.exists(filename_s):
                print("\nSkip existing " + filename_s)
            else:
                np.savez_compressed(
                    filename_s,
                    X_int=X_int[0:i, :],
                    X_cat_t=np.transpose(X_cat[0:i, :]),
                    y=y[0:i],
                )
                print("\nSaved " + npzfile + "_{0}.npz!".format(split))

        if dataset_multiprocessing:
            resultDay[split] = i
            convertDictsDay[split] = convertDicts_day
            return
        else:
            return i

    @staticmethod
    def _transform_line(line, rand_u, sub_sample_rate):
        line = line.split('\t')
        # set missing values to zero
        for j in range(len(line)):
            if (line[j] == '') or (line[j] == '\n'):
                line[j] = '0'
        # sub-sample data by dropping zero targets, if needed
        target = np.int32(line[0])
        if target == 0 and rand_u < sub_sample_rate:
            return None

        return (target,
                np.array(line[1:14], dtype=np.int32),
                np.array(
                    list(map(lambda x: int(x, 16), line[14:])),
                    dtype=np.int32)
                )

    def clear_items(self):
        self.data_items = defaultdict(dict)
        self.ln_emb = None
        self.m_den = None
        self.n_emb = None

    def process_data(self):
        _, total_per_file = self.get_counts()
        self.split_dataset(total_per_file)

        convertDicts = self.process_files(
            self.datafile,
            self.total_file,
            total_per_file, self.dataset_multiprocessing
        )

        # dictionary files
        counts = np.zeros(26, dtype=np.int32)
        # create dictionaries
        for j in range(26):
            for i, x in enumerate(convertDicts[j]):
                convertDicts[j][x] = i
            dict_file_j = self.d_path + self.d_file + \
                "_fea_dict_{0}.npz".format(j)
            if not os.path.exists(dict_file_j):
                np.savez_compressed(
                    dict_file_j,
                    unique=np.array(list(convertDicts[j]), dtype=np.int32)
                )
            counts[j] = len(convertDicts[j])
        # store (uniques and) counts
        count_file = self.d_path + self.d_file + "_fea_count.npz"
        if not os.path.exists(count_file):
            np.savez_compressed(count_file, counts=counts)

        # process all splits
        if self.dataset_multiprocessing:
            processes = [
                Process(
                    target=CriteoDataProcessor.processCriteoAdData,
                    name="processCriteoAdData:%i" % i,
                    args=(self.npzfile, i, self.days, convertDicts)
                ) for i in range(0, self.days)
            ]
            for process in processes:
                process.start()
            for process in processes:
                process.join()
        else:
            for i in range(self.days):
                CriteoDataProcessor.processCriteoAdData(
                    self.npzfile, i, self.days, convertDicts)

        return self.concat_data(self.output_file)

    def split_dataset(self, total_per_file):
        # split into days (simplifies code later on)
        file_id = 0
        boundary = total_per_file[file_id]
        nf = open(self.npzfile + "_" + str(file_id), "w")
        with open(str(self.datafile)) as f:
            for j, line in enumerate(f):
                if j == boundary:
                    nf.close()
                    file_id += 1
                    nf = open(self.npzfile + "_" + str(file_id), "w")
                    boundary += total_per_file[file_id]
                nf.write(line)
        nf.close()

    def get_counts(self):
        if os.path.exists(self.total_file):
            with np.load(self.total_file) as data:
                total_per_file = list(data["total_per_file"])
            total_count = np.sum(total_per_file)
            print("Skipping counts per file (already exist)")
        else:
            total_count = 0
            total_per_file = []
            print("Reading data from path=%s" % (self.datafile))
            with open(str(self.datafile)) as f:
                for _ in f:
                    total_count += 1
            total_per_file.append(total_count)
            # reset total per file due to split
            num_data_per_split, extras = divmod(total_count, self.days)
            total_per_file = [num_data_per_split] * self.days
            for j in range(extras):
                total_per_file[j] += 1
        return total_count, total_per_file

    def process_files(
        self, total_count,
        total_file, total_per_file, dataset_multiprocessing
    ):
        convertDicts = [{} for _ in range(26)]
        if dataset_multiprocessing:
            resultDay = Manager().dict()
            convertDictsDay = Manager().dict()
            processes = [Process(target=CriteoDataProcessor._process_one_file,
                                 name="process_one_file:%i" % i,
                                 args=(self.npzfile + "_{0}".format(i),
                                       self.npzfile,
                                       i,
                                       total_per_file[i],
                                       dataset_multiprocessing,
                                       self.days
                                       ),
                                 kwargs={
                                     "sub_sample_rate": self.sub_sample_rate,
                                     "convertDictsDay": convertDictsDay,
                                     "resultDay": resultDay
                                 }) for i in range(0, self.days)]
            for process in processes:
                process.start()
            for process in processes:
                process.join()
            for day in range(self.days):
                total_per_file[day] = resultDay[day]
                print("Constructing convertDicts Split: {}".format(day))
                convertDicts_tmp = convertDictsDay[day]
                for i in range(26):
                    for j in convertDicts_tmp[i]:
                        convertDicts[i][j] = 1
        else:
            for i in range(self.days):
                total_per_file[i] = CriteoDataProcessor._process_one_file(
                    self.npzfile + "_{0}".format(i),
                    self.npzfile,
                    i,
                    total_per_file[i],
                    dataset_multiprocessing,
                )
                # report and save total into a file
        total_count = np.sum(total_per_file)
        if not os.path.exists(total_file):
            np.savez_compressed(total_file, total_per_file=total_per_file)
        print("Total number of samples:", total_count)
        print("Divided into days/splits:\n", total_per_file)
        return convertDicts

    def processCriteoAdData(npzfile, i, days, convertDicts):
        filename_i = npzfile + "_{0}_processed.npz".format(i)

        if os.path.exists(filename_i):
            print("Using existing " + filename_i, end="\n")
            return
        print("Not existing " + filename_i)
        with np.load(npzfile + "_{0}.npz".format(i)) as data:
            # categorical features
            # Approach 2a: using pre-computed dictionaries
            X_cat_t = np.zeros(data["X_cat_t"].shape)
            for j in range(days):
                for k, x in enumerate(data["X_cat_t"][j, :]):
                    X_cat_t[j, k] = convertDicts[j][x]
            # continuous features
            X_int = data["X_int"]
            X_int[X_int < 0] = 0

            np.savez_compressed(
                filename_i,
                X_cat=np.transpose(X_cat_t),  # transpose of the data
                X_int=X_int,
                y=data["y"],
            )
        print("Processed " + filename_i, end="\n")

    def concat_data(self, o_filename):
        print("Concatenating multiple days into %s.npz file" %
              str(self.d_path + o_filename))

        # load and concatenate data
        for i in range(self.days):
            filename_i = self.npzfile + "_{0}_processed.npz".format(i)
            with np.load(filename_i) as data:
                if i == 0:
                    X_cat = data["X_cat"]
                    X_int = data["X_int"]
                    y = data["y"]
                else:
                    X_cat = np.concatenate((X_cat, data["X_cat"]))
                    X_int = np.concatenate((X_int, data["X_int"]))
                    y = np.concatenate((y, data["y"]))
            print("Loaded day:", i, "y = 1:", len(
                y[y == 1]), "y = 0:", len(y[y == 0]))

        with np.load(self.d_path + self.d_file + "_fea_count.npz") as data:
            counts = data["counts"]
        print("Loaded counts!")

        np.savez_compressed(
            self.d_path + o_filename + ".npz",
            X_cat=X_cat,
            X_int=X_int,
            y=y,
            counts=counts,
        )
        self.m_den = X_int.shape[1]  # den_fea
        self.n_emb = len(counts)
        # enforce maximum limit on number of vectors per embedding
        if self.max_ind_range > 0:
            self.ln_emb = np.array(list(map(
                lambda x: x if x < self.max_ind_range else self.max_ind_range,
                counts))
            )
        else:
            self.ln_emb = np.array(counts)

        np.savez_compressed(self.d_path + o_filename + "_data_description.npz",
                            m_den=self.m_den,
                            n_emb=self.n_emb,
                            ln_emb=self.ln_emb)
        return self.d_path + o_filename + ".npz"

    def load_data_description(self):
        if not os.path.exists(str(self.d_path + self.output_file + ".npz")):
            assert False, "data not processed"

        with np.load(self.d_path + self.output_file
                     + "_data_description.npz") as data:
            self.m_den = data["m_den"]
            self.n_emb = data["n_emb"]
            self.ln_emb = data["ln_emb"]

    def load(self):
        if not os.path.exists(str(self.d_path + self.output_file + ".npz")):
            assert False, "data not processed"

        # pre-process data if needed
        # WARNNING: when memory mapping is used we get a collection of files
        print("Reading pre-processed data=%s" %
              (str(self.d_path + self.output_file + ".npz")))
        file = str(self.d_path + self.output_file + ".npz")

        # get a number of samples per day
        total_file = self.d_path + self.d_file + "_day_count.npz"
        with np.load(total_file) as data:
            total_per_file = data["total_per_file"]
        # compute offsets per file
        offset_per_file = np.array([0] + [x for x in total_per_file])
        for i in range(self.days):
            offset_per_file[i + 1] += offset_per_file[i]

        # load and preprocess data
        with np.load(file) as data:
            X_int = data["X_int"]  # continuous  feature
            X_cat = data["X_cat"]  # categorical feature
            y = data["y"]          # target
            counts = data["counts"]

        self.m_den = X_int.shape[1]  # den_fea
        self.n_emb = len(counts)
        # enforce maximum limit on number of vectors per embedding
        if self.max_ind_range > 0:
            self.ln_emb = np.array(list(map(
                lambda x: x if x < self.max_ind_range else self.max_ind_range,
                self.counts))
            )
        else:
            self.ln_emb = np.array(counts)

        indices = self.permute_data(len(y), offset_per_file)
        print("Sparse fea = %d, Dense fea = %d" % (self.n_emb, self.m_den))

        for split, indxs in indices.items():
            self.data_items[split]["X_int"] = [X_int[i] for i in indxs]
            self.data_items[split]["X_cat"] = [X_cat[i] for i in indxs]
            self.data_items[split]["y"] = [y[i] for i in indxs]

    def permute_data(self, length, offset_per_file):
        indices = np.arange(length)
        indices = np.array_split(indices, offset_per_file[1:-1])

        # randomize train data (per day)
        if self.randomize == "day":  # or randomize == "total":
            for i in range(len(indices) - 1):
                indices[i] = np.random.permutation(indices[i])
            print("Randomized indices per day ...")

        train_indices = np.concatenate(indices[:-1])
        test_indices = indices[-1]
        test_indices, val_indices = np.array_split(test_indices, 2)

        # randomize train data (across days)
        if self.randomize == "total":
            train_indices = np.random.permutation(train_indices)
            print("Randomized indices across days ...")

        return {'train': train_indices,
                'val': val_indices,
                'test': test_indices}

    def dataset(self, split):
        return CriteoDataset(
            max_ind_range=self.max_ind_range,
            **self.data_items[split]
        )

    @property
    def collate_fn(self):
        return collate_wrapper_criteo_length
