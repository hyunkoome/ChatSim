#!/bin/bash

# file_list 배열 선언
file_list=(
#   "segment-11379226583756500423_6230_810_6250_810_with_camera_labels"
   "segment-12879640240483815315_5852_605_5872_605_with_camera_labels"
   "segment-14424804287031718399_1281_030_1301_030_with_camera_labels"
   "segment-17761959194352517553_5448_420_5468_420_with_camera_labels"
   "segment-14333744981238305769_5658_260_5678_260_with_camera_labels"
   "segment-16470190748368943792_4369_490_4389_490_with_camera_labels"
   "segment-4058410353286511411_3980_000_4000_000_with_camera_labels"
   "segment-13196796799137805454_3036_940_3056_940_with_camera_labels"
   "segment-10247954040621004675_2180_000_2200_000_with_camera_labels"
   "segment-13469905891836363794_4429_660_4449_660_with_camera_labels"
   "segment-1172406780360799916_1660_000_1680_000_with_camera_labels"
   "segment-10061305430875486848_1080_000_1100_000_with_camera_labels"
   "segment-14869732972903148657_2420_000_2440_000_with_camera_labels"
   "segment-16646360389507147817_3320_000_3340_000_with_camera_labels"
   "segment-13238419657658219864_4630_850_4650_850_with_camera_labels"
   "segment-15270638100874320175_2720_000_2740_000_with_camera_labels"
   "segment-15349503153813328111_2160_000_2180_000_with_camera_labels"
#   "segment-15868625208244306149_4340_000_4360_000_with_camera_labels"
#   "segment-16608525782988721413_100_000_120_000_with_camera_labels"
#   "segment-3425716115468765803_977_756_997_756_with_camera_labels"
#   "segment-3988957004231180266_5566_500_5586_500_with_camera_labels"
#   "segment-9385013624094020582_2547_650_2567_650_with_camera_labels"
#   "segment-8811210064692949185_3066_770_3086_770_with_camera_labels"
#   "segment-10275144660749673822_5755_561_5775_561_with_camera_labels"
#   "segment-10676267326664322837_311_180_331_180_with_camera_labels"
#   "segment-13142190313715360621_3888_090_3908_090_with_camera_labels"
#   "segment-14348136031422182645_3360_000_3380_000_with_camera_labels"
#   "segment-15365821471737026848_1160_000_1180_000_with_camera_labels"
#   "segment-13085453465864374565_2040_000_2060_000_with_camera_labels"
#   "segment-14004546003548947884_2331_861_2351_861_with_camera_labels"
#   "segment-15221704733958986648_1400_000_1420_000_with_camera_labels"
#   "segment-16345319168590318167_1420_000_1440_000_with_camera_labels"
)

# 실행 모드 확인
mode=$1

if [[ "$mode" == "train" ]]; then
    echo "Running in training mode."
    for case_name in "${file_list[@]}"
    do
        echo "Running case: $case_name"
        CUDA_VISIBLE_DEVICES=0 python scripts/run.py --config-name=wanjinyou_big \
            dataset_name=waymo_multi_view case_name=$case_name \
            exp_name=exp_coeff_0.3 dataset.shutter_coefficient=0.3 mode=train_hdr_shutter +work_dir=$(pwd)
    done
elif [[ "$mode" == "render" ]]; then
    echo "Running in rendering mode."
    for case_name in "${file_list[@]}"
    do
        echo "Running case: $case_name"
        CUDA_VISIBLE_DEVICES=0 python scripts/run.py --config-name=wanjinyou_big \
            dataset_name=waymo_multi_view case_name=$case_name \
            exp_name=exp_coeff_0.3 mode=render_wide_angle_hdr_shutter is_continue=true +work_dir=$(pwd)
    done
else
    echo "Invalid mode. Please use 'train' or 'render'."
    exit 1
fi

echo "All cases have been executed."
