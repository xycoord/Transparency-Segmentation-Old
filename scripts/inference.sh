inference_single_image(){
input_rgb_path="../data_sample/kitti3d_000025.png"
output_dir="outputs"
pretrained_model_path="Bingxin/Marigold" # your checkpoint here
ensemble_size=10

cd ..
cd run

CUDA_VISIBLE_DEVICES=0 python run_inference.py \
    --input_rgb_path $input_rgb_path \
    --output_dir $output_dir \
    --pretrained_model_path $pretrained_model_path \
    --ensemble_size $ensemble_size
    }




