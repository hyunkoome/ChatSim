# Multi-camera images to HDR skydome

This is an auxiliary library for ChatSim, predicting skydome environment HDR map from single or multi-view images.

## Installation

```bash
conda activate chatsim
pip install -r requirements.txt
```

**imageio requirement:** To read .exr file, you need FreeImage library. You can obtain it with either:

- download in terminal:
 
    ```imageio_download_bin freeimage```
- download in python CLI: 

    ```import imageio; imageio.plugins.freeimage.download()```

### install this repo as a package

```
python setup.py develop
mkdir dataset # create a folder for dataset
```

## Data
### HDRI data
We use HDRI data crawled from [Poly Hevean](https://polyhaven.com). All HDRIs subject to [CC0 License](https://polyhaven.com/license). 

You can download our selected and divided HDRIs from [Google Drive](https://drive.google.com/file/d/1dU4Bce3dpcr6lnBJkyG2OKl1GmU8BviQ/view?usp=drive_link), and put it under the `dataset` folder, naming it `HDRi_download`

Or you want to download the HDRIs yourself, you can use the following command.
```
python mc_to_sky/utils/downloader.py 1k outdoor exr
```
This will download all outdoor category HDRI in 1k resolution with extension `.exr`. Not all outdoor HDRIs are suitable for training,
we mannually select and split them into train / val set. See [here](https://drive.google.com/drive/folders/1ossgXhGBwnJ5CpMP8B7Ngm0ZmahUu3nM?usp=drive_link).


### HoliCity
We select outdoor samples from [HoliCity](https://holicity.io/) Panorama dataset. Please download the [resized panorama](https://drive.google.com/file/d/1XkEydyPePKODRUNeWhFcOQ5g-fgqbpgk/view?usp=drive_link), [resized panorama mask](https://drive.google.com/file/d/1qzF8w67qiqg_Im53xuKf6WirBOFfj3oq/view?usp=drive_link), [cropped images](https://drive.google.com/file/d/1I97TtkGXPCjMOUr4RD1L115XnEd4q6iI/view?usp=drive_link), [meta info](https://drive.google.com/drive/folders/1zbgwNBT-4Pvp-kgXXrOqpC0KhcwPyQ8J?usp=drive_link) and unzip them into `dataset` folder.

If you want to process the panorama data yourself, you can download the original [HoliCity](https://holicity.io/) Panorama Dataset from their [Google Drive](https://drive.google.com/file/d/1Qhy2axPtcYG6lKwalE3CStY_eLpUj9nR/edit). Then, you need to resize the panorama and crop perspective view images with `mc_to_sky/tools/holicity/holicity_preprocess.py`. 

Finally, an expected data structure should be like this:
```
dataset
├── HDRi_download 
│   ├── train
│   └── val
├── holicity_meta_info
│   └── selected_sample.json
├── holicity_crop_multiview 
├── holicity_pano_sky_resized_64 
└── holicity_pano_sky_resized_64_mask 
```

```shell
ln -s /home/hyunkoo/Dataset/NAS/nfsRoot/Datasets/Waymo_Datasets/ChatSim/skydome_lighting_dataset/dataset dataset
```
## Usage

Create log dir and link 
```shell
cd foreground/mclight/skydome_lighting/mc_to_sky
ln -s /home/hyunkoo/Dataset/NAS/nfsRoot/Train_Results/ChatSim/skydome_lighting/logs logs
```

### Stage 1: Train LDR to HDR autoencoder
**Train**

```bash
python mc_to_sky/tools/train.py -y mc_to_sky/config/stage1/skymodel_peak_residual.yaml
```
Then we use the trained model to predict pseduo HDRI GT for HoliCity dataset. You can find a `config.yaml` and the best checkpoint inside the log folder, we denote them `STAGE_1_CONFIG` and `STAGE_1_BEST_CKPT` respectively.

```bash
python mc_to_sky/tools/holicity/holicity_generate_gt.py -y mc_to_sky/config/stage1/skymodel_peak_residual.yaml -c STAGE_1_BEST_CKPT --target_dir dataset/holicity_pano_hdr

python mc_to_sky/tools/holicity/holicity_generate_gt.py -y mc_to_sky/config/stage1/skymodel_peak_residual.yaml -c /home/hyunkoo/DATA/HDD8TB/Add_Objects_DrivingScense/ChatSim/chatsim/foreground/mclight/skydome_lighting/mc_to_sky/logs/stage1_recon_pano_peak_residual_wb_adjust_1222_234457/lightning_logs/version_0/checkpoints/epoch=369-val_loss=1.25.ckpt --target_dir dataset/holicity_pano_hdr
 
```
Now `dataset/holicity_pano_hdr` stores the pseduo HDRI GT for holicity dataset.

**Test**

You can validate and test your checkpoint by

```bash
python mc_to_sky/tools/test.py -y mc_to_sky/config/stage1/skymodel_peak_residual.yaml -c STAGE_1_BEST_CKPT
python mc_to_sky/tools/test.py -y mc_to_sky/config/stage1/skymodel_peak_residual.yaml -c /home/hyunkoo/DATA/HDD8TB/Add_Objects_DrivingScense/ChatSim/chatsim/foreground/mclight/skydome_lighting/mc_to_sky/logs/stage1_recon_pano_peak_residual_wb_adjust_1222_234457/lightning_logs/version_0/checkpoints/epoch=369-val_loss=1.25.ckpt
```
results are stored in `<logdir>/lightning_logs/version_i/visualization`

### Stage 2: Train HDRI predictor from multiview images
**Train**

First edit line 43 of `mc_to_sky/config/stage2/multi_view_avg.yaml`, put `STAGE_1_BEST_CKPT` as the value. Then conduct the stage 2 training. 
```bash
python mc_to_sky/tools/train.py -y mc_to_sky/config/stage2/multi_view_avg.yaml
```
**Test**

You can also validate and test your checkpoint by
```bash
python mc_to_sky/tools/test.py -y mc_to_sky/config/stage2/multi_view_avg.yaml -c STAGE_2_BEST_CKPT

python mc_to_sky/tools/test.py -y mc_to_sky/config/stage2/multi_view_avg.yaml -c /home/hyunkoo/DATA/HDD8TB/Add_Objects_DrivingScense/ChatSim/chatsim/foreground/mclight/skydome_lighting/mc_to_sky/logs/stage2_multi_camera_hdri_prediction_1223_201420/lightning_logs/version_0/checkpoints/epoch=89-val_loss=0.13.ckpt


```
where `STAGE_2_BEST_CKPT` refers to the new training log's best checkpoint.

**Infer**

We directly adopt the model trained on HoliCity for the inference on Waymo dataset.
```bash
python mc_to_sky/tools/infer.py -y mc_to_sky/config/stage2/multi_view_avg.yaml -c STAGE_2_BEST_CKPT -i IMAGE_FOLDER -o OUPUT_FOLDER

python mc_to_sky/tools/infer.py -y mc_to_sky/config/stage2/multi_view_avg.yaml \
-c /home/hyunkoo/DATA/HDD8TB/Add_Objects_DrivingScense/ChatSim/chatsim/foreground/mclight/skydome_lighting/mc_to_sky/logs/stage2_multi_camera_hdri_prediction_1223_201420/lightning_logs/version_0/checkpoints/epoch=89-val_loss=0.13.ckpt \
-i /home/hyunkoo/DATA/HDD8TB/Add_Objects_DrivingScense/ChatSim/data/waymo_multi_view/segment-1172406780360799916_1660_000_1680_000_with_camera_labels/images \
-o /home/hyunkoo/DATA/HDD8TB/Add_Objects_DrivingScense/ChatSim/data/waymo_multi_view/segment-1172406780360799916_1660_000_1680_000_with_camera_labels/images_skydome

```

The `IMAGE_FOLDER` should contain continuous image data, for example, pictures from three views should be put together and follow the order in `STAGE_2_CONFIG['view_setting']['view_dis']`. Note that `IMAGE_FOLDER` can include multiple frames, an examplar image sequence can be `[frame_1_front, frame_1_front_left, frame_1_front_right, frame_2_front, frame_2_front_left, frame_2_front_right, ...]`. For our waymo dataset, you can point `IMAGE_FOLDER` to `data/waymo_multi_view/$SCENE_NAME/images` in our ChatSim.


We further provide `mc_to_sky/tools/infer_waymo_batch.py` which add another loop on the scene-level. 
```bash
python mc_to_sky/tools/infer_waymo_batch.py -y mc_to_sky/config/stage2/multi_view_avg.yaml -c STAGE_2_BEST_CKPT --waymo_scenes_dir WAYMO_SCENE_DIR -o OUPUT_FOLDER

python mc_to_sky/tools/infer_waymo_batch.py \
-y mc_to_sky/config/stage2/multi_view_avg.yaml \
-c /home/hyunkoo/DATA/HDD8TB/Add_Objects_DrivingScense/ChatSim/chatsim/foreground/mclight/skydome_lighting/mc_to_sky/logs/stage2_multi_camera_hdri_prediction_1223_201420/lightning_logs/version_0/checkpoints/epoch=89-val_loss=0.13.ckpt \
-w /home/hyunkoo/DATA/HDD8TB/Add_Objects_DrivingScense/ChatSim/data/waymo_multi_view \
-o /home/hyunkoo/DATA/NAS/nfsRoot/Datasets/Waymo_Datasets/ChatSim/waymo_multi_view_hdr_skydome
```

- `/home/hyunkoo/DATA/NAS/nfsRoot/Datasets/Waymo_Datasets/ChatSim/waymo_multi_view_hdr_skydome` 여기서 생성된 파일들은 ..
- 여기 [Download Skydome HDRI](../../../../README.md)에서 아래(`https://huggingface.co/datasets/yifanlu/Skydome_HDRI`)에서 다운로드 한, 파일과 동일함
- 따라서, `ln -s` 명령어를 통해서 링크.. 하길...
```shell
cd $ChatSim_HOME
cd data
 
cd /home/hyunkoo/DATA/HDD8TB/Add_Objects_DrivingScense/ChatSim/data
ln -s /home/hyunkoo/DATA/NAS/nfsRoot/Datasets/Waymo_Datasets/ChatSim/waymo_multi_view_hdr_skydome waymo_skydome
```


where we suppose the `WAYMO_SCENE_DIR` have the following structure
```
WAYMO_SCENE_DIR
├── segment-10061305430875486848_1080_000_1100_000_with_camera_labels
│   ├── ...
│   └── images # also follows the specific image order
├── segment-10247954040621004675_2180_000_2200_000_with_camera_labels
│   ├── ...
│   └── images
├── segment-10275144660749673822_5755_561_5775_561_with_camera_labels
│   ├── ...
│   └── images
└── ...
```

## Pretrain
download the pretrain models (`STAGE_1_BEST_CKPT` and `STAGE_2_BEST_CKPT`) from [Google Drive](https://drive.google.com/file/d/1vc8LeChk-wH4YTYEOGbxfng8TB6RBYL7/view?usp=drive_link)
