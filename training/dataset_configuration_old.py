import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import sys
sys.path.append("..")

from dataloader.sceneflow_loader import StereoDataset
from torch.utils.data import DataLoader
from dataloader import transforms
import os


# Get Dataset Here
def prepare_dataset(data_name,
                    datapath=None,
                    trainlist=None,
                    vallist=None,
                    batch_size=1,
                    test_batch=1,
                    datathread=4,
                    logger=None):
    
    # set the config parameters
    dataset_config_dict = dict()
    
    if data_name == 'sceneflow':
        train_transform_list = [transforms.ToTensor(),]
        train_transform = transforms.Compose(train_transform_list)

        val_transform_list = [transforms.ToTensor(),]
        val_transform = transforms.Compose(val_transform_list)
        
        train_dataset = StereoDataset(data_dir=datapath,train_datalist=trainlist,test_datalist=vallist,
                                dataset_name='SceneFlow',mode='train',transform=train_transform)
        test_dataset = StereoDataset(data_dir=datapath,train_datalist=trainlist,test_datalist=vallist,
                                dataset_name='SceneFlow',mode='val',transform=val_transform)

    img_height, img_width = train_dataset.get_img_size()


    datathread=4
    if os.environ.get('datathread') is not None:
        datathread = int(os.environ.get('datathread'))
    
    if logger is not None:
        logger.info("Use %d processes to load data..." % datathread)

    train_loader = DataLoader(train_dataset, batch_size = batch_size, \
                            shuffle = True, num_workers = datathread, \
                            pin_memory = True)

    test_loader = DataLoader(test_dataset, batch_size = test_batch, \
                            shuffle = False, num_workers = datathread, \
                            pin_memory = True)
    
    num_batches_per_epoch = len(train_loader)
    
    
    dataset_config_dict['num_batches_per_epoch'] = num_batches_per_epoch
    dataset_config_dict['img_size'] = (img_height,img_width)
    
    
    return (train_loader,test_loader),dataset_config_dict

def Disparity_Normalization(disparity):
    min_value = torch.min(disparity)
    max_value = torch.max(disparity)
    normalized_disparity = ((disparity -min_value)/(max_value-min_value+1e-5) - 0.5) * 2    
    return normalized_disparity

def resize_max_res_tensor(input_tensor,is_disp=False,recom_resolution=768):
    assert input_tensor.shape[1]==3
    original_H, original_W = input_tensor.shape[2:]
    
    downscale_factor = min(recom_resolution/original_H,
                           recom_resolution/original_W)
    
    resized_input_tensor = F.interpolate(input_tensor,
                                         scale_factor=downscale_factor,mode='bilinear',
                                         align_corners=False)
    
    if is_disp:
        return resized_input_tensor * downscale_factor
    else:
        return resized_input_tensor