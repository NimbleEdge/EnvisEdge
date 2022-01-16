import abc
import sys

import numpy as np
import torch
from fedrec.preprocessor import DLRMPreprocessor
from fedrec.utilities import registry
from torch import nn, sigmoid
from torch.nn.parameter import Parameter


def xavier_init(layer: nn.Linear):
    # initialize the weights
    with torch.no_grad():
        # custom Xavier input, output or two-sided fill
        mean = 0.0
        std_dev = np.sqrt(2 / (layer.out_features + layer.in_features))
        W = np.random.normal(mean, std_dev, size=(
            layer.out_features, layer.in_features)).astype(np.float32)
        std_dev = np.sqrt(1 / layer.out_features)  # np.sqrt(2 / (m + 1))
        bt = np.random.normal(
            mean, std_dev, size=layer.out_features).astype(np.float32)
        layer.weight.set_(torch.tensor(W))
        layer.bias.set_(torch.tensor(bt))
        return layer
### define dlrm in PyTorch ###


@registry.load("model", "dlrm")
class DLRM_Net(nn.Module):
    Preproc = DLRMPreprocessor

    def create_mlp(self, ln, sigmoid_layer):
        # build MLP layer by layer
        layers = [xavier_init(nn.Linear(ln[0], ln[1], True))]
        for in_f, out_f in zip(ln[1:], ln[2:]):
            layers += [registry.construct('sigmoid_layer',
                                          {'name': sigmoid_layer}),
                       xavier_init(nn.Linear(in_f, out_f, True))]
        return torch.nn.Sequential(*layers)

    def create_emb(self, m, ln, emb_dict, weighted_pooling=None):
        emb_l = nn.ModuleList()
        v_W_l = []
        for i in range(0, ln.size):
            # construct embedding operator

            if ((emb_dict.get("custom", None) is not None)
                    and (ln[i] > emb_dict["threshold"])):
                EE = registry.construct("embedding", emb_dict["custom"],
                                        num_embeddings=ln[i],
                                        embedding_dim=m)
            else:
                EE = registry.construct("embedding", emb_dict["base"],
                                        num_embeddings=ln[i],
                                        embedding_dim=m)
            if weighted_pooling is None:
                v_W_l.append(None)
            else:
                v_W_l.append(torch.ones(ln[i], dtype=torch.float32))
            emb_l.append(EE)
        return emb_l, v_W_l

    def __init__(
        self,
        preprocessor: DLRMPreprocessor,
        arch_feature_emb_size=None,
        arch_mlp_bot=None,
        arch_mlp_top=None,
        arch_interaction_op=None,
        arch_interaction_itself=False,
        sigmoid_bot="relu",
        sigmoid_top="relu",
        loss_weights=None,
        loss_threshold=0.0,
        ndevices=-1,
        embedding_types={},
        weighted_pooling=None,
        loss_function="bce"
    ):
        super(DLRM_Net, self).__init__()
        self.preproc = preprocessor

        if (
            (arch_feature_emb_size is not None)
            and (self.preproc.ln_emb is not None)
            and (arch_mlp_bot is not None)
            and (arch_mlp_top is not None)
            and (arch_interaction_op is not None)
        ):

            # save arguments
            self.ndevices = ndevices
            self.m_spa = arch_feature_emb_size
            self.ln_emb = self.preproc.ln_emb
            self.ln_bot = arch_mlp_bot + [self.m_spa]
            self.output_d = 0
            self.parallel_model_batch_size = -1
            self.parallel_model_is_not_prepared = True
            self.arch_interaction_op = arch_interaction_op
            self.arch_interaction_itself = arch_interaction_itself
            self.loss_threshold = loss_threshold
            self.loss_function = loss_function

            # create variables for QR embedding if applicable
            self.emb_dict = embedding_types

            ### parse command line arguments ###
            num_fea = self.ln_emb.size + 1  # num sparse + num dense features
            m_den = self.preproc.m_den
            self.ln_bot[0] = m_den
            if arch_interaction_op == "dot":
                if arch_interaction_itself:
                    num_int = (num_fea * (num_fea + 1)) // 2 + self.ln_bot[-1]
                    offset = 1
                else:
                    num_int = (num_fea * (num_fea - 1)) // 2 + self.ln_bot[-1]
                    offset = 0
                self.index_tensor_i = torch.tensor(
                    [i for i in range(num_fea)
                     for j in range(i + offset)]
                )
                self.index_tensor_j = torch.tensor(
                    [j for i in range(num_fea)
                     for j in range(i + offset)]
                )
            elif arch_interaction_op == "cat":
                num_int = num_fea * self.ln_bot[-1]
            else:
                sys.exit(
                    "ERROR: --arch-interaction-op="
                    + arch_interaction_op
                    + " is not supported"
                )
            self.ln_top = [num_int] + arch_mlp_top
            # self.sanity_check()

            # create operators
            self.emb_l, w_list = self.create_emb(
                self.m_spa, self.ln_emb, self.emb_dict, weighted_pooling)

            if weighted_pooling is not None and weighted_pooling != "fixed":
                self.weighted_pooling = "learned"
                self.v_W_l = nn.ParameterList()
                for w in w_list:
                    self.v_W_l.append(Parameter(w))
            else:
                self.weighted_pooling = weighted_pooling
                self.v_W_l = w_list

            self.bot_l = self.create_mlp(self.ln_bot, sigmoid_bot)
            self.top_l = self.create_mlp(self.ln_top, sigmoid_top)

            # specify the loss function
            if self.loss_function == "mse":
                self.loss_fn = torch.nn.MSELoss(reduction="mean")
            elif self.loss_function == "bce":
                self.loss_fn = torch.nn.BCEWithLogitsLoss(
                    reduction="mean", pos_weight=loss_weights)
            else:
                sys.exit(
                    "ERROR: --loss_function="
                    + self.loss_function
                    + " is not supported"
                )

    def toGPU(self):
        # Custom Model-Data Parallel
        # the mlps are replicated and use data parallelism, while
        # the embeddings are distributed and use model parallelism
        if self.ndevices > 1:
            self.emb_l, self.v_W_l = self.create_emb(
                self.m_spa, self.ln_emb, self.emb_dict, self.weighted_pooling)
        else:
            if self.weighted_pooling == "fixed":
                for k, w in enumerate(self.v_W_l):
                    self.v_W_l[k] = w.cuda()

    def sanity_check(self):
        # sanity check: feature sizes and mlp dimensions must match
        if ((self.emb_dict.get('custom', None) is not None)
                and (self.emb_dict['custom']['name'] == 'qr_emb')):
            if (self.emb_dict["custom"]['qr_operation'] == "concat"
                    and 2 * self.m_spa != self.ln_bot[-1]):
                sys.exit(
                    "ERROR: 2 arch-sparse-feature-size "
                    + str(2 * self.m_spa)
                    + " does not match last dim of bottom mlp "
                    + str(self.ln_bot[-1])
                    + " (note that the last dim of bottom mlp"
                    + "must be 2x the embedding dim)"
                )
            if (self.qr_dict['qr_operation'] != "concat"
                    and self.m_spa != self.ln_bot[-1]):
                sys.exit(
                    "ERROR: arch-sparse-feature-size "
                    + str(self.m_spa)
                    + " does not match last dim of bottom mlp "
                    + str(self.ln_bot[-1])
                )
        else:
            if self.m_spa != self.ln_bot[-1]:
                sys.exit(
                    "ERROR: arch-sparse-feature-size "
                    + str(self.m_spa)
                    + " does not match last dim of bottom mlp "
                    + str(self.ln_bot[-1])
                )

    def apply_mlp(self, x, layers):
        return layers(x)

    def apply_emb(self, lS_o, lS_i, emb_l, v_W_l):
        ly = [None]*len(lS_i)
        merged_embeddings = zip(emb_l, lS_i, lS_o, v_W_l)
        for i, (emb, lsi, lso, vwl) in enumerate(merged_embeddings):
            per_sample_weights = vwl.gather(
                0, lsi) if vwl is not None else None
            ly[i] = emb(
                lsi,
                lso.long(),
                per_sample_weights=per_sample_weights,
            )
        return ly

    def interact_features(self, x, ly):

        if self.arch_interaction_op == "dot":
            # concatenate dense and sparse features
            (batch_size, d) = x.shape
            T = torch.cat([x] + ly, dim=1).view((batch_size, -1, d))
            # perform a dot product
            Z = torch.bmm(T, torch.transpose(T, 1, 2))
            Zflat = Z[:, self.index_tensor_i, self.index_tensor_j]
            # concatenate dense features and interactions
            R = torch.cat([x] + [Zflat], dim=1)
        elif self.arch_interaction_op == "cat":
            # concatenation features (into a row vector)
            R = torch.cat([x] + ly, dim=1)
        else:
            sys.exit(
                "ERROR: --arch-interaction-op="
                + self.arch_interaction_op
                + " is not supported"
            )

        return R

    def forward(self, dense_x, lS_o, lS_i):
        # process dense features (using bottom mlp), resulting in a row vector
        x = self.apply_mlp(dense_x, self.bot_l)
        ly = self.apply_emb(lS_o, lS_i, self.emb_l, self.v_W_l)
        z = self.interact_features(x, ly)
        out = self.apply_mlp(z, self.top_l)
        # clamp output if needed
        if 0.0 < self.loss_threshold and self.loss_threshold < 1.0:
            out = torch.clamp(out, min=self.loss_threshold,
                              max=(1.0 - self.loss_threshold))
        return out

    def get_scores(self, logits):
        return sigmoid(logits)

    def loss(self, logits, true_label):
        if self.loss_function == "mse":
            return self.loss_fn(self.get_scores(logits), true_label)
        elif self.loss_function == "bce":
            return self.loss_fn(logits, true_label)
