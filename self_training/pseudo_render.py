'''
Render psueod mesh into pseudo depth.
by: Jiayu Yang

'''

import os, re
os.environ["PYOPENGL_PLATFORM"] = "egl"
import argparse
import numpy as np
import imagesize
import trimesh
import pyrender
from pyrender.constants import RenderFlags

from utils import *

parser = argparse.ArgumentParser(description='Render pseudo mesh into pseudo depth maps')

parser.add_argument('--dataset_dir', type=str, help='path to dataset')
parser.add_argument('--mesh_dir', type=str, help='path to pseudo mesh')
parser.add_argument('--pseudo_depth_dir', type=str, help='path to output pseudo depth dataset')
parser.add_argument('--pseudo_height', type=int, default=128, help='height of pseudo depth map')
parser.add_argument('--pseudo_width', type=int, default=160, help='width of pseudo depth map')

args = parser.parse_args()

print("\n############### Render pseudo depth ###############")
print(args)

if not os.path.isdir(args.pseudo_depth_dir):
    os.mkdir(args.pseudo_depth_dir)

# Read test list
viewlist = args.dataset_dir+"/scan_list_train.txt"
with open(viewlist) as f:
    scans = f.readlines()
    scans = [line.rstrip() for line in scans]

scans_idx = [int(re.search(r'\d+', scan).group()) for scan in scans]

for scan_idx in scans_idx:

    print("########## scan{} ##########".format(scan_idx))

    input_path = os.path.join(args.mesh_dir,'cvpmvsnet{:03d}_l3.ply'.format(scan_idx))
    cam_path = os.path.join(args.dataset_dir,'Cameras')
    img_path = os.path.join(args.dataset_dir,'Rectified',"scan{}".format(scan_idx))
    output_path = os.path.join(args.pseudo_depth_dir,"Depths","scan{}_train".format(scan_idx))

    # Read view list
    cam_txts = os.listdir(cam_path)
    view_list = [int(view[:8]) for view in cam_txts if view.startswith('0')]
    view_list.sort()

    # Read camera parameters
    print("Reading cameras...")
    intrinsics = []
    extrinsics = []
    depth_min = []
    depth_max = []
    for view in view_list:
        print(view,end=' ',flush=True)
        camera_file = os.path.join(cam_path,'{:08d}_cam.txt'.format(view))
        intrinsics_tmp, extrinsics_tmp, depth_min_tmp, depth_max_tmp = readCamFile(camera_file)
        intrinsics.append(intrinsics_tmp)
        extrinsics.append(extrinsics_tmp)
        depth_min.append(depth_min_tmp)
        depth_max.append(depth_max_tmp)
    print('\n')

    # Read mesh
    print("Reading mesh...")
    print(input_path)
    mesh = trimesh.load(input_path)

    # Initialize pyrender scene
    print("Initializing pyrender scene...")
    pyrender_mesh = pyrender.Mesh.from_trimesh(mesh, smooth=False)
    scene = pyrender.Scene()
    scene.add(pyrender_mesh)

    # Initialize egl offscreen renderer
    print("Initializing offscreen renderer...")
    r = pyrender.OffscreenRenderer(int(args.pseudo_width), int(args.pseudo_height))
    flags = RenderFlags.SKIP_CULL_FACES # Add flags to skip face culling.

    # render depth
    print("----- rendering depth map -----")
    for view in view_list:

        print("View"+str(view),end=";")

        # Read camera
        K = intrinsics[view]
        RT = extrinsics[view]

        # Convert camera to fit pseudo depth size (128x160)
        K[:2,:]/=8.0
        K[0,2]-=20
        K[1,2]-=11

        # Set up the camera -- z-axis away from the scene, x-axis right, y-axis up
        znear = depth_min[view]
        zfar = depth_max[view]
        camera = pyrender.IntrinsicsCamera(K[0,0], K[1,1], K[0,2], K[1,2], znear=0, zfar=zfar, name=None)

        # Convert CV Pose into OpenGL view matrix
        cvTogl2 = np.array([
            [ 1.0, 1.0, 1.0, 1.0],
            [-1.0,-1.0,-1.0,-1.0],
            [-1.0,-1.0,-1.0,-1.0],
            [ 1.0, 1.0, 1.0, 1.0],
        ])

        camera_pose = np.linalg.inv(cvTogl2*RT)

        camera_node = pyrender.Node(camera=camera,matrix=camera_pose)
        scene.add_node(camera_node)

        # Render the scene
        color, depth = r.render(scene, flags=flags)

        scene.remove_node(camera_node)

        # Filter out depth
        depth_min_mask = depth<depth_min[view]
        depth_max_mask = depth>depth_max[view]
        # depth[depth_min_mask] = 0
        depth[depth_max_mask] = 0
        depth[depth<0] = 0

        # Save Depth
        depth_out_path = os.path.join(output_path,"depth_map_{:04d}.pfm".format(view))
        write_pfm(depth_out_path,depth)
        write_depth_img(depth_out_path+".png", depth)
        print(";Depth",depth_out_path)

    r.delete()

    print("scan {} done.".format(scan_idx))