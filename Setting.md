# 1. Prepair dataset

## 1-1. For ChatSim

```shell
cd ChatSim
mkdir -p data/waymo_tfrecords/1.4.2

cd ChatSim/data_utils
bash link_tfrecods.sh
```

```shell
cd ChatSim/data
ln -s /home/hyunkoo/DATA/NAS/nfsRoot/Datasets/Waymo_Datasets/ChatSim/waymo_multi_view waymo_multi_view
ln -s /home/hyunkoo/DATA/NAS/nfsRoot/Datasets/Waymo_Datasets/ChatSim/Skydome_HDRI/waymo_skydome waymo_skydome
ln -s /home/hyunkoo/DATA/NAS/nfsRoot/Datasets/Waymo_Datasets/ChatSim/Blender_3D_assets/assets blender_assets
```

## 1-2. For mcnerf
```shell
cd chatsim/background/mcnerf
ln -s ../../../data .
```

# 2. Prepair Packages

## 2-1. For ChatSim

### Step 1: Setup environment
```bash
conda create -n chatsim python=3.9 git-lfs
conda activate chatsim
```

Taking `torch-2.1.0+cu121` for example.
```shell
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt --force-reinstall --no-deps
imageio_download_bin freeimage
```

Cmake 버전 체크
```shell
cmake --version
```
CMake 3.18 or higher is required.  

오래된 cmake 제거
```shell
sudo apt remove cmake
```

최신 CMake 다운로드 및 설치
CMake를 직접 다운로드하여 설치합니다:
```shell
# 최신 CMake 다운로드
wget https://github.com/Kitware/CMake/releases/download/v3.27.4/cmake-3.27.4-linux-x86_64.sh

# 실행 권한 추가
chmod +x cmake-3.27.4-linux-x86_64.sh

# CMake 설치
sudo ./cmake-3.27.4-linux-x86_64.sh --prefix=/usr/local --exclude-subdir
```

설치된 CMake 버전을 확인
```shell
cmake --version
```
출력된 버전이 3.18 이상인지 확인

환경 변수에서 CMake 경로 확인
```shell
which cmake
```

환경 변수 수정: .bashrc 또는 .zshrc에 최신 CMake 경로를 추가
```shell
export PATH=/usr/local/bin:$PATH
```

새 경로 추가 방법
예를 들어, 새 경로 /opt/cmake/bin을 추가하려면 아래처럼 수정하면 됨

```shell
export PATH="/usr/local/cuda/bin:/opt/cmake/bin:$PATH"
```

```shell
source ~/.bashrc
```

## 2-2. For mcnerf

The development of this project is primarily based on LibTorch.
### Step 1. Install dependencies

For Debian based Linux distributions:
```
sudo apt install zlib1g-dev
```

For Arch based Linux distributions:
```
sudo pacman -S zlib
```

### Step 2. Download pre-compiled LibTorch
Taking `torch-2.1.0+cu121` for example.
```shell
cd chatsim/background/mcnerf
cd External

# modify the verison if you use a different pytorch installation
wget https://download.pytorch.org/libtorch/cu121/libtorch-cxx11-abi-shared-with-deps-2.1.0%2Bcu121.zip
unzip ./libtorch-cxx11-abi-shared-with-deps-2.1.0+cu121.zip 
rm ./libtorch-cxx11-abi-shared-with-deps-2.1.0+cu121.zip
```

#### Compile
The lowest g++ version is 7.5.0. 

check g++ version
```shell
g++ --version
```

yaml-cpp 라이브러리 생성:
```shell
cd External/yaml-cpp
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug
make

cmake .. -DCMAKE_BUILD_TYPE=Release
make
```

```shell
cd chatsim/background/mcnerf
cmake . -B build
cmake --build build --target main --config RelWithDebInfo -j
```

If the mcnerf code is modified, the last two lines should always be executed.

Create train folder
```shell
cd chatsim/background/mcnerf
ln -s /home/hyunkoo/DATA/NAS/nfsRoot/Train_Results/ChatSim/mcnerf/outputs outputs
ln -s /home/hyunkoo/DATA/NAS/nfsRoot/Train_Results/ChatSim/mcnerf/exp exp
```

For training 
```shell
cd chatsim/background/mcnerf
bash train_or_render.sh train
```

For testing 
```shell
cd chatsim/background/mcnerf
bash train_or_render.sh render
```



## 2-3. For 3D Gaussians Splatting

3DGS has much faster inference speed, higher rendering quality. But the HDR sky is not enabled in this case.

Installing 3DGS requires that your CUDA NVCC version matches your pytorch cuda version.

```bash
# make CUDA (nvcc) version consistent with the pytorch CUDA version.

# first check your CUDA (nvcc) version
nvcc -V # for example: Build cuda_11.8.r11.8

# CUDA 12.1: pip 로 설치했으면, skip
conda install pytorch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 pytorch-cuda=12.1 -c pytorch -c nvidia

pip install -r requirements.txt
imageio_download_bin freeimage

cd chatsim/background/gaussian-splatting/
pip install submodules/simple-knn
```

## 2-4 For Inpainting tools

#### Step 1: Setup Video Inpainting
```bash
cd ../inpainting/Inpaint-Anything/
python -m pip install -e segment_anything
pip install beautifulsoup4
gdown https://drive.google.com/drive/folders/1wpY-upCo4GIW4wVPnlMh_ym779lLIG2A -O pretrained_models --folder
gdown https://drive.google.com/drive/folders/1SERTIfS7JYyOOmXWujAva4CDQf-W7fjv -O pytracking/pretrain --folder
```

#### Step 2: Setup Image Inpainting
```bash
cd ../latent-diffusion
pip install -e git+https://github.com/CompVis/taming-transformers.git@master#egg=taming-transformers
pip install -e git+https://github.com/openai/CLIP.git@main#egg=clip
pip install -e .

# download pretrained ldm
wget -O models/ldm/inpainting_big/last.ckpt https://heibox.uni-heidelberg.de/f/4d9ac7ea40c64582b7c9/?dl=1
```

## 2-5 For Blender Software and our Blender Utils

We tested with [Blender 3.5.1](https://download.blender.org/release/Blender3.5/blender-3.5.1-linux-x64.tar.xz). Note that Blender 3+ requires Ubuntu version >= 20.04.

#### Step 1: Install Blender software
```bash
#cd ../../Blender
cd ../../../foreground/Blender/
wget https://download.blender.org/release/Blender3.5/blender-3.5.1-linux-x64.tar.xz

tar -xvf blender-3.5.1-linux-x64.tar.xz
rm blender-3.5.1-linux-x64.tar.xz
```

#### Step 2: Install blender utils for Blender's python
locate the internal Python of Blender, for example, `blender-3.5.1-linux-x64/3.5/python/bin/python3.10`

```bash
export blender_py=$PWD/blender-3.5.1-linux-x64/3.5/python/bin/python3.10

cd utils

# 패키지 설치
$blender_py -m pip install --upgrade pip setuptools
$blender_py -m pip install -r requirements.txt

# install dependency (use the -i https://pypi.tuna.tsinghua.edu.cn/simple if you are in the Chinese mainland)
# 중국 PyPI 미러를 사용해야 하는 경우
$blender_py -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 개발 모드 설치
$blender_py setup.py develop
cd ../../
```

Setting dataset folder
```shell
cd Blender/utils
ln -s ../../../../data/blender_assets assets
```

## 2-6 For Trajectory Tracking Module (optional)
If you want to get smoother and more realistic trajectories, you can install the trajectory module and change the parameter `motion_agent-motion_tracking` to True in .yaml file. For installation (both code and pre-trained model), you can run the following commands in the terminal. This requires Pytorch >= 1.13.
```bash
pip install frozendict gym==0.26.2 stable-baselines3[extra] protobuf==3.20.1
#pip install frozendict gym==0.26.2 stable-baselines3[extra] protobuf==3.19.6

cd chatsim/foreground
git clone --recursive git@github.com:MARMOTatZJU/drl-based-trajectory-tracking.git -b v1.0.0

cd drl-based-trajectory-tracking
source setup-minimum.sh
```

Then when the parameter `motion_agent-motion_tracking` is set as True, each trajectory will be tracked by this module to make it smoother and more realistic.


## 2-7 For McLight (optional)
If you want to train the skydome model, follow the README in `chatsim/foreground/mclight/skydome_lighting/readme.md`. You can download our provided skydome HDRI in the next section and start the simulation.

```shell
cd ChatSim/chatsim/foreground/mclight/skydome_lighting
pip install -r requirements.txt

imageio_download_bin freeimage
python setup.py develop

ln -s /home/hyunkoo/DATA/NAS/nfsRoot/Datasets/Waymo_Datasets/ChatSim/skydome_lighting_dataset/dataset dataset
cd mc_to_sky
ln -s /home/hyunkoo/DATA/NAS/nfsRoot/Train_Results/ChatSim/skydome_lighting/logs logs
```



# 3. Prepair Results: Create results directories

## 3-1. For ChatSim
```shell
cd ChatSim
ln -s /home/hyunkoo/DATA/NAS/nfsRoot/Train_Results/ChatSim/chatsim results
```


#### Start simulation
Set the API to an environment variable. Also, set `OPENAI_API_BASE` if you have network issues (especially in China mainland).
```bash
export OPENAI_API_KEY=<your api key>
```

Now you can start the simulation with
```bash
python main.py -y ${CONFIG YAML} \
               -p ${PROMPT} \
               [-s ${SIMULATION NAME}]
```

- `${CONFIG YAML}` specifies the scene information, and yamls are stored in `config` folder. e.g. `config/waymo-1137.yaml`.

- `${PROMPT}` is your input prompt, which should be wrapped in quotation marks. e.g. `add a straight driving car in the scene`.

- `${SIMULATION NAME}` determines the name of the folder when saving results. default `demo`.

You can try
```bash
# if you train nerf
python main.py -y config/waymo-1137.yaml -p "Add a Benz G in front of me, driving away fast."
# if you train 3DGS
python main.py -y config/3dgs-waymo-1137.yaml -p "Add a Benz G in front of me, driving away fast."
```

```shell
cd ChatSim
ln -s /home/hyunkoo/DATA/NAS/nfsRoot/Train_Results/ChatSim/chatsim_results results
bash scripts/run_main.sh /home/hyunkoo/DATA/HDD8TB/Add_Objects_DrivingScense/ChatSim/.env
```

The rendered results are saved in `results/1137_demo_%Y_%m_%d_%H_%M_%S`. Intermediate files are saved in `results/cache/1137_demo_%Y_%m_%d_%H_%M_%S` for debug and visualization if `save_cache` are enabled in `config/waymo-1137.yaml`.

#### Config file explanation
`config/waymo-1137.yaml` contains a detailed explanation for each entry. We will give some extra explanation. Suppose the yaml is read into `config_dict`:

- `config_dict['scene']['is_wide_angle']` determines the rendering view. If set to `True`, we will expand Waymo's intrinsics (width -> 3 x width) to render wide-angle images. Also note that `is_wide_angle = True` comes with `rendering_mode = 'render_wide_angle_hdr_shutter'`; `is_wide_angle = False` comes with `rendering_mode = 'render_hdr_shutter'`

- `config_dict['scene']['frames']` the frame number for rendering.

- `config_dict['agents']['background_rendering_agent']['nerf_quiet_render']` will determine whether to print the output of mcnerf to the terminal. Set to `False` for debug use.

- `config_dict['agents']['foreground_rendering_agent']['use_surrounding_lighting']` defines whether we use the surrounding lighting. Currently `use_surrounding_lighting = True` only takes effect when merely one vehicle is added, because HDRI is a global illumination in Blender. It is difficult to set a separate HDRI for each car. `use_surrounding_lighting = True` can also lead to slow rendering, since it will call nerf `#frame` times. We set it to `False` in each default yaml. 

- `config_dict['agents']['foreground_rendering_agent']['skydome_hdri_idx']` is the filename (w.o. extension) we choose from `data/waymo_skydome/${SCENE_NAME}/`. It is the skydome HDRI estimation from the first frame(`'000'`) by default, but you can manually select a better estimation from another frame. To view the HDRI, we recommend the [VERIV](https://github.com/mcrescas/veriv) for vscode and [tev](https://github.com/Tom94/tev) for desktop environment.


