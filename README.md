# Self-supervised-CVP-MVSNet
Self-supervised Learning of Depth Inference for Multi-view Stereo (CVPR 2021)

This repository extend the original [CVP-MVSNet](https://github.com/JiayuYANG/CVP-MVSNet) with unsupervised training and self-training.

## How to use

### 0. Pre-requisites
Please refer to the original [CVP-MVSNet](https://github.com/JiayuYANG/CVP-MVSNet) for basic usage.

Pre-requisites for unsupervised initialization and self-training:
* [open3d](http://www.open3d.org/docs/release/getting_started.html)
* [trimesh](https://github.com/mikedh/trimesh)
* [pyrender](https://pyrender.readthedocs.io/en/latest/install/index.html#installpyopengl) 

### 1. Unsupervised initialization
Coming soon...

### 2. Self-training
Code and scripts for self-training can be found in the `CVP-MVSNet/self-training` folder. 
* `self-training.sh`: Shell script to run following code and generate pseudo depth from a given checkpoint.
* `pseudo_fusion.py`: Pseudo label filtering and Multi-view pseudo label fusion.
* `surface_reconstruction.py`: Generate pseudo mesh by Screened Poisson Surface Reconstruction.
* `pseudo_render.py`: Render pseudo mesh into new pseudo depth maps.

To generate pseudo depth given a base checkpoint:

`sh self-training.sh`

Pseudo depth will be generated in `self-training/outputs_self_training_itr$ITR/pseudo_depth_128/` folder.

The generated pseudo depth can be linked into `dataset/dtu-train-128/` and replace the existing `Depths` folder using either `mv` or `ln -s`.

Next iteration of self-training can be start by `train.sh`.

## Acknowledgment

If you find this project useful for your research, please cite:

```
@inproceedings{Yang_2021_CVPR,
  author = {Yang, Jiayu and Alvarez, Jose M. and Liu, Miaomiao},
  title={Self-supervised Learning of Depth Inference for Multi-view Stereo},
  booktitle = {The IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  year={2021}
}

@InProceedings{Yang_2020_CVPR,
    author = {Yang, Jiayu and Mao, Wei and Alvarez, Jose M. and Liu, Miaomiao},
    title = {Cost Volume Pyramid Based Depth Inference for Multi-View Stereo},
    booktitle = {The IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
    year = {2020}
}
```