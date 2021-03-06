from numpy.core import numeric
from torch.utils.data.dataset import Dataset
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import torch
import albumentations as A
from albumentations.pytorch.transforms import ToTensorV2

import numpy as np
from PIL import Image
import utils
import cv2
import matplotlib.pyplot as plt


from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


class Transforms: 
    def __init__(self, transforms: A.Compose):
        self.transforms = transforms

    def __call__(self, img, *args, **kwargs):
        return self.transforms(image=np.array(img))['image']


class DepthTransform(Dataset):
    def __init__(self, img_path, transform):
        self.transforms = A.Compose([A.Crop(x_min=345, y_min=365, x_max=1120, y_max=1000)]) #
        self.img_list,__ = utils.list_files(img_path, ".png")

    def __len__(self):
        return len(self.img_list)

    def __getitem__(self, idx):
        img = np.asarray(Image.open(self.img_list[idx]))
        # print(img.min(), img.max())
        img = (img-300)/(500-300)
        img = img.clip(min=0, max=1)
        # print(img)
        data = self.transforms(image=img)
        # print(data['image'])
        # print(data['image'][0].min(),data['image'][0].max())
        return data['image']

# NOTE: this to test if the albumentations also remaps to 0-1
# class DepthTransform(Dataset):
#     def __init__(self, img_path, transform):
#         self.transforms = A.Compose([A.Crop(x_min=345, y_min=365, x_max=1120, y_max=1000), ToTensorV2()])
#         self.img_list,__ = utils.list_files(img_path, ".png")

#     def __len__(self):
#         return len(self.img_list)

#     def __getitem__(self, idx):
#         image = cv2.imread(self.img_list[idx])
#         print(image.min(), image.max())
#         image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#         image = image/255
#         data = self.transforms(image=image)
#         print(data['image'][0].min(),data['image'][0].max())
#         return data['image']

if __name__ == "__main__":

    data_path ="/zhome/3b/d/154066/repos/GALIROOT/data/l515_lab_1410/img"
    depth_path ="/zhome/3b/d/154066/repos/GALIROOT/data/l515_lab_1410/depth"

    # Train dataset
    a_transform = A.Compose([
        A.Crop(x_min=345, y_min=365, x_max=1120, y_max=1000)])

    dataset = datasets.ImageFolder(f"{data_path}", transform = transforms.Compose([Transforms(a_transform), transforms.ToTensor()]))
    
    depth_dataset = DepthTransform(depth_path,a_transform)
    image_loader = torch.utils.data.DataLoader(dataset,
                        batch_size=10,
                        num_workers=0,
                        shuffle=False)
    depth_loader = torch.utils.data.DataLoader(depth_dataset,
                            batch_size=10,
                            num_workers=0,
                            shuffle=False)
    mean = 0.
    std = 0.
    nb_samples = 0
    for data, _ in image_loader:
        batch_samples = data.size(0)
        data = data.view(batch_samples, data.size(1), -1)
        mean += data.mean(2).sum(0)
        std += data.std(2).sum(0)
        nb_samples += batch_samples

    mean /= nb_samples
    std /= nb_samples
    print("\nImages:")
    print(mean)
    print(std)

    # NOTE: this to test if the albumentations also remaps to 0-1
    # mean = 0.
    # std = 0.
    # nb_samples = 0
    # for data in depth_loader:
    #     batch_samples = data.size(0)
    #     data = data.view(batch_samples, data.size(1), -1)
    #     data_float = data.type(torch.FloatTensor)
    #     mean += data_float.mean(2).sum(0)
    #     std += data_float.std(2).sum(0)
    #     nb_samples += batch_samples

    # mean /= nb_samples
    # std /= nb_samples
    # print("\nDepth:")
    # print(mean)
    # print(std)

    mean = 0.
    std = 0.
    nb_samples = 0
    for data in depth_loader:
        batch_samples = data.size(0)
        data = data.view(batch_samples, -1)
        data_float = data.type(torch.FloatTensor)
        mean += data_float.mean(1).sum(0)
        std += data_float.std(1).sum(0)
        nb_samples += batch_samples


    mean /= nb_samples
    std /= nb_samples
    print("\nDepth images:")
    print(mean)
    print(std)
