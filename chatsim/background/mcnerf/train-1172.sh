cmake . -B build
wait
cmake --build build --target main --config RelWithDebInfo -j
wait
python scripts/run.py --config-name=wanjinyou_big \
dataset_name=waymo_multi_view case_name=segment-1172406780360799916_1660_000_1680_000_with_camera_labels \
exp_name=exp_coeff_0.15 dataset.shutter_coefficient=0.15 mode=train_hdr_shutter +work_dir=$(pwd) 