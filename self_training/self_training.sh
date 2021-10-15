# Self-training script
ITR="1"

DATASET_DIR="../dataset/dtu-train-nodepth-1200/"
LOAD_CKPT_DIR="../checkpoints/unsupervised/model_000010.ckpt"
LOG_DIR="../logs/"
FUSIBILE_EXE="../fusion/fusibile"

EST_DEPTH_DIR="./outputs_self_training_itr$ITR/est_depth/"
PSEUDO_PC_DIR="./outputs_self_training_itr$ITR/pseudo_pc/"
PSEUDO_MESH_DIR="./outputs_self_training_itr$ITR/pseudo_mesh/"
PSUEDO_DEPTH_DIR="./outputs_self_training_itr$ITR/pseudo_depth_128/"

##### Step 1: Inference on training set #####
python3 ../eval.py \
--info="inference_training_set_$ITR" \
--mode="test" \
--dataset_root=$DATASET_DIR \
--imgsize=1200 \
--nsrc=4 \
--nscale=5 \
--batch_size=1 \
--loadckpt=$LOAD_CKPT_DIR \
--logckptdir=$CKPT_DIR \
--loggingdir=$LOG_DIR \
--outdir=$EST_DEPTH_DIR

##### Step 2: Fuse pseudo depth #####
python2 pseudo_fusion.py \
--dtu_test_root=$DATASET_DIR \
--depth_folder=$EST_DEPTH_DIR \
--out_folder=$PSEUDO_PC_DIR \
--fusibile_exe_path=$FUSIBILE_EXE \
--prob_threshold=0.8 \
--disp_threshold=0.13 \
--num_consistent=3

##### Step 3: Surface reconstruction #####
python3 surface_reconstruction.py \
--pc_dir=$PSEUDO_PC_DIR \
--mesh_out_dir=$PSEUDO_MESH_DIR \
--spsr_depth=11 \
--trimming_threshold=0.05

##### Step 4: Render pseudo depth #####
export EGL_DEVICE_ID=0
python3 pseudo_render.py \
--dataset_dir=$DATASET_DIR \
--mesh_dir=$PSEUDO_MESH_DIR \
--pseudo_depth_dir=$PSUEDO_DEPTH_DIR \
--pseudo_height=128 \
--pseudo_width=160 \

