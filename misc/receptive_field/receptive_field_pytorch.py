# -*- coding: utf-8 -*-
import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.nn.init as init
import torch.nn.functional as F
import torchvision
from torchvision.models import resnet18, resnet34, resnet50, vgg16


def compute_RF_numerical(net, img_np):
    '''
    @param net: Pytorch network
    @param img_np: numpy array to use as input to the networks, it must be full of ones and with the correct
    shape.
    '''

    def weights_init(m):
        classname = m.__class__.__name__
        if classname.find('Conv') != -1:
            # print('classname:', classname)
            m.weight.data.fill_(1)
            if m.bias is not None:
                # print('classname:', classname)
                m.bias.data.fill_(0)


    net.apply(weights_init)
    img_ = Variable(torch.from_numpy(img_np).float(), requires_grad=True)
    out_cnn = net(img_)
    out_shape = out_cnn.size()
    ndims = len(out_cnn.size())
    grad = torch.zeros(out_cnn.size())
    l_tmp = []
    for i in xrange(ndims):
        if i == 0 or i == 1:  # batch or channel
            l_tmp.append(0)
        else:
            l_tmp.append(out_shape[i] / 2)

    grad[tuple(l_tmp)] = 1
    out_cnn.backward(gradient=grad)
    grad_np = img_.grad[0, 0].data.numpy()
    idx_nonzeros = np.where(grad_np != 0)
    RF = [np.max(idx) - np.min(idx) + 1 for idx in idx_nonzeros]

    return RF

###########################################################

mycnn = resnet50()

img_np = np.ones((1, 3, 224, 224))
print 'numerical RF', compute_RF_numerical(mycnn, img_np)
