'''
Run surface reconstruction and trimming on pseudo point clouds.
by: Jiayu Yang

'''

import os
import argparse
import xml.etree.ElementTree as ET
import numpy as np
import open3d as o3d

parser = argparse.ArgumentParser(description='Run SPSR and related processing on given point clouds')

parser.add_argument('--pc_dir', type=str, help='path to input point cloud files')
parser.add_argument('--mesh_out_dir', type=str, help='path to output mesh files')
parser.add_argument('--spsr_depth', type=int, default=10, help='SPSR depth')
parser.add_argument('--trimming_threshold', type=float, default=0.06, help='trimming threshold')

args = parser.parse_args()

print("\n############### Surface reconstruction ###############")
print(args)

if not os.path.isdir(args.mesh_out_dir):
    os.mkdir(args.mesh_out_dir)

pc_lists = [f for f in os.listdir(args.pc_dir) if f.endswith('ply')]
pc_lists.sort()
for pc_file in pc_lists:
    print("############# {} #############".format(pc_file))

    # Read point cloud
    print("Reading point cloud...")
    pcd = o3d.io.read_point_cloud(os.path.join(args.pc_dir,pc_file))

    # Compute normal
    print("Recompute normal of the point cloud...")
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

    # Surface reconstruction
    print("Surface reconstruction...")
    with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug) as cm:
        mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=12)

    # Trimming
    print('Trimming...')
    trimming_threshold = np.quantile(densities,args.trimming_threshold)
    vertices_to_remove = densities < np.float32(trimming_threshold)
    mesh.remove_vertices_by_mask(vertices_to_remove)

    # Save mesh plys
    print("Writing mesh...")
    output_path = os.path.join(args.mesh_out_dir,pc_file)
    print(output_path)
    o3d.io.write_triangle_mesh(output_path, mesh)