from sklearn.cluster import AgglomerativeClustering
import numpy as np
from utility import construct_doc_matrix


class Evaluator():
    @staticmethod
    def compute_f1(dataset, bpr_optimizer, start_cluster_size, incr_size, stop_threshhold ):
        """
        perform Hierarchy Clustering on doc embedding matrix
        for name disambiguation
        use cluster-level mean F1 for evaluation
        """
        D_matrix = construct_doc_matrix(bpr_optimizer.paper_latent_matrix,
                                        dataset.paper_list)
        # true_cluster_size = len(set(dataset.label_list))
        true_cluster_size = start_cluster_size
        y_pred = AgglomerativeClustering(n_clusters = true_cluster_size,
                                         linkage = "average",
                                         affinity = "cosine").fit_predict(D_matrix)

        # true_label_dict = {}
        # for idx, true_lbl in enumerate(dataset.label_list):
        #     if true_lbl not in true_label_dict:
        #         true_label_dict[true_lbl] = [idx]
        #     else:
        #         true_label_dict[true_lbl].append(idx)

        start_label_dict = {}
        for idx, start_lbl in enumerate(y_pred):
            if start_lbl not in start_label_dict:
                start_label_dict[start_lbl] = [idx]
            else:
                start_label_dict[start_lbl].append(idx)

        temp_f1 = 0
        while True:
            true_cluster_size = true_cluster_size + incr_size
            if true_cluster_size >= len(dataset.coauthor_list):
                break
                
            y_pred = AgglomerativeClustering(n_clusters = true_cluster_size,
                                         linkage = "average",
                                         affinity = "cosine").fit_predict(D_matrix)
            predict_label_dict = {}
            for idx, pred_lbl in enumerate(y_pred):
                if pred_lbl not in predict_label_dict:
                    predict_label_dict[pred_lbl] = [idx]
                else:
                    predict_label_dict[pred_lbl].append(idx)

            # print 'true label :', true_label_dict
            # print 'predict :', y_pred
            # compute cluster-level F1
            # let's denote C(r) as clustering result and T(k) as partition (ground-truth)
            # construct r * k contingency table for clustering purpose 
            r_k_table = []
            for v1 in predict_label_dict.itervalues():
                k_list = []
                for v2 in start_label_dict.itervalues():
                    N_ij = len(set(v1).intersection(v2))
                    k_list.append(N_ij)
                r_k_table.append(k_list)
            r_k_matrix = np.array(r_k_table)
            r_num = int(r_k_matrix.shape[0])

            # compute F1 for each row C_i
            sum_f1 = 0.0
            for row in xrange(0, r_num):
                row_sum = np.sum(r_k_matrix[row,:])
                if row_sum != 0:
                    max_col_index = np.argmax(r_k_matrix[row,:])
                    row_max_value = r_k_matrix[row, max_col_index]
                    prec = float(row_max_value) / row_sum
                    col_sum = np.sum(r_k_matrix[:, max_col_index])
                    rec = float(row_max_value) / col_sum
                    row_f1 = float(2 * prec * rec) / (prec + rec)
                    sum_f1 += row_f1

            average_f1 = float(sum_f1) / r_num
            print 'average_f1 :', average_f1
            if abs((average_f1 - temp_f1)/average_f1) < stop_threshhold:
                break
            print 'diff :', abs((average_f1 - temp_f1)/average_f1)
            temp_f1 = average_f1
        
        print 'final size :', true_cluster_size
        print 'final pred label :', y_pred
        cluster_list = []
        item_list = []
        for v in predict_label_dict.itervalues():
            item_list = []
            for i in v:
                item_list.append(dataset.paper_dict[i+1])
            cluster_list.append(item_list)
        print 'final paper list :' , cluster_list   
        return average_f1
