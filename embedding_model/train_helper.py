from utility import save_embedding


class TrainHelper():
    @staticmethod
    def helper(num_epoch, dataset, bpr_optimizer,
               pp_sampler, pd_sampler, dd_sampler,
               eval_f1, sampler_method):

        bpr_optimizer.init_model(dataset)
        if sampler_method == "uniform":
            print 'into uniform method'
            print 'num_epoch: ', num_epoch
            print 'dataset.num_nnz: ', dataset.num_nnz
            for _ in xrange(0, num_epoch):
                bpr_loss = 0.0
                for _ in xrange(0, dataset.num_nnz):
                    """
                    update embedding in person-person network
                    update embedding in person-document network
                    update embedding in doc-doc network
                    """
                    for i, j, t in pp_sampler.generate_triplet_uniform(dataset):
                        # print 'pp_sample'
                        bpr_optimizer.update_pp_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_pp_loss(i, j, t)

                    for i, j, t in pd_sampler.generate_triplet_uniform(dataset):
                        # print 'pd_sample'
                        bpr_optimizer.update_pd_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_pd_loss(i, j, t)

                    for i, j, t in dd_sampler.generate_triplet_uniform(dataset):
                        # print 'dd_sample'
                        bpr_optimizer.update_dd_gradient(i, j, t)
                        bpr_loss += bpr_optimizer.compute_dd_loss(i, j, t)

                average_loss = float(bpr_loss) / dataset.num_nnz
                print "average bpr loss is " + str(average_loss)
                # average_f1 = eval_f1.compute_f1(dataset, bpr_optimizer)
                # print 'f1 is ' + str(average_f1)
                # print
            average_f1 = eval_f1.compute_f1(dataset, bpr_optimizer,len(dataset.coauthor_list)/10,1,0.001)
            print 'f1 is ' + str(average_f1)
            print            

        elif sampler_method == "reject":
            for _ in xrange(0, num_epoch):
                #bpr_loss = 0.0
                for _ in xrange(0, dataset.num_nnz):
                    """
                    update embedding in person-person network
                    update embedding in person-document network
                    update embedding in doc-doc network
                    """
                    for i, j, t in pp_sampler.generate_triplet_reject(dataset, bpr_optimizer):
                        bpr_optimizer.update_pp_gradient(i, j, t)
                        #bpr_loss += bpr_optimizer.compute_pp_loss(i, j, t)

                    for i, j, t in pd_sampler.generate_triplet_reject(dataset, bpr_optimizer):
                        bpr_optimizer.update_pd_gradient(i, j, t)
                        #bpr_loss += bpr_optimizer.compute_pd_loss(i, j, t)

                    for i, j, t in dd_sampler.generate_triplet_reject(dataset, bpr_optimizer):
                        bpr_optimizer.update_dd_gradient(i, j, t)
                        #bpr_loss += bpr_optimizer.compute_dd_loss(i, j, t)

        elif sampler_method == "adaptive":
            for _ in xrange(0, num_epoch):
                #bpr_loss = 0.0
                for _ in xrange(0, dataset.num_nnz):
                    """
                    update embedding in person-person network
                    update embedding in person-document network
                    update embedding in doc-doc network
                    """
                    for i, j, t in pp_sampler.generate_triplet_adaptive(dataset, bpr_optimizer):
                        bpr_optimizer.update_pp_gradient(i, j, t)
                        #bpr_loss += bpr_optimizer.compute_pp_loss(i, j, t)

                    for i, j, t in pd_sampler.generate_triplet_adaptive(dataset, bpr_optimizer):
                        bpr_optimizer.update_pd_gradient(i, j, t)
                        #bpr_loss += bpr_optimizer.compute_pd_loss(i, j, t)

                    for i, j, t in dd_sampler.generate_triplet_adaptive(dataset, bpr_optimizer):
                        bpr_optimizer.update_dd_gradient(i, j, t)
                        #bpr_loss += bpr_optimizer.compute_dd_loss(i, j, t)

        save_embedding(bpr_optimizer.paper_latent_matrix,
                       dataset.paper_list, bpr_optimizer.latent_dimen)
