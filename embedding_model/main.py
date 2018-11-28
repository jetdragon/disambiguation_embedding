import json
import pandas as pd
from pandas.io.json import json_normalize
import parser_json
import embedding
import train_helper
import sampler
import eval_metric
import argparse


def parse_args():
    """
    parse the embedding model arguments
    """
    parser_arg = argparse.ArgumentParser(description =
                                         "run embedding for name disambiguation")
    parser_arg.add_argument("file_path1", help = 'input file name1')
    # parser_arg.add_argument("file_path2", help = 'input file name2')
    parser_arg.add_argument("latent_dimen", type = int, default = 20,
                            help = 'number of dimension in embedding')
    parser_arg.add_argument("alpha", type = float, default = 0.02,
                            help = 'learning rate')
    parser_arg.add_argument("matrix_reg", type = float, default = 0.01,
                            help = 'matrix regularization parameter')
    parser_arg.add_argument("num_epoch", type = int, default = 100,
                            help = "number of epochs for SGD inference")
    parser_arg.add_argument("sampler_method", help = "sampling approach")
    return parser_arg.parse_args()


def main(args):
    """
    pipeline for representation learning for all papers for a given name reference
    """
    # print args.file_path1
    # print args.file_path2
    # print args.sampler_method
    with open(args.file_path1, 'r') as f1:
        json_file1 = json.load(f1)
        df1 = json_normalize(json_file1)

    # with open(args.file_path2, 'r') as f2:
    #     json_file2 = json.load(f2)
    #     df2 = json_normalize(json_file2)

    # print 'read file done.' 

    for key, value in df1.iteritems():
        # if key == 'hong_yan_wang':       
        print 'begin process user (', key, ') ************'
        # dataset = parser_json.DataSet(key, value, df2)
        dataset = parser_json.DataSet(key, value)
        dataset.reader_arnetminer()
        if dataset.num_nnz < 1000000:
            bpr_optimizer = embedding.BprOptimizer(args.latent_dimen, args.alpha,
                                                args.matrix_reg)
            pp_sampler = sampler.CoauthorGraphSampler()
            pd_sampler = sampler.BipartiteGraphSampler()
            dd_sampler = sampler.LinkedDocGraphSampler()
            eval_f1 = eval_metric.Evaluator()

            run_helper = train_helper.TrainHelper()
            run_helper.helper(args.num_epoch, dataset, bpr_optimizer,
                            pp_sampler, pd_sampler, dd_sampler,
                            eval_f1, args.sampler_method)


if __name__ == "__main__":
    args = parse_args()
    main(args)
