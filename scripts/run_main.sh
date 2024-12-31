#!/bin/bash

#python main.py -y ${CONFIG YAML} \
#               -p ${PROMPT} \
#               [-s ${SIMULATION NAME}]
#- `${CONFIG YAML}` specifies the scene information, and yamls are stored in `config` folder. e.g. `config/waymo-1137.yaml`.
#- `${PROMPT}` is your input prompt, which should be wrapped in quotation marks. e.g. `add a straight driving car in the scene`.
#- `${SIMULATION NAME}` determines the name of the folder when saving results. default `demo`.

# setup-minimum.sh가 위치한 디렉토리
SETUP_SCRIPT_DIR="./chatsim/foreground/drl-based-trajectory-tracking"
SETUP_SCRIPT_PATH="${SETUP_SCRIPT_DIR}/setup-minimum.sh"

# setup-minimum.sh 실행
if [ -f "$SETUP_SCRIPT_PATH" ]; then
  echo "Running setup-minimum.sh..."
  pushd "$SETUP_SCRIPT_DIR" > /dev/null  # 해당 디렉토리로 이동
  source ./setup-minimum.sh             # 스크립트 실행
  popd > /dev/null                      # 원래 디렉토리로 복귀
else
  echo "Error: setup-minimum.sh not found at $SETUP_SCRIPT_PATH"
  exit 1
fi

# PYTHONPATH 확인 (디버깅용)
echo "PYTHONPATH after setup-minimum.sh: $PYTHONPATH"

# .env 파일 경로 설정
ENV_PATH="/home/hyunkoo/DATA/HDD8TB/Journal/ChatSim/.env"

# .env 파일에서 환경 변수 불러오기
if [ -f "$ENV_PATH" ]; then
  echo "Loading environment variables from $ENV_PATH"
  export $(grep -v '^#' "$ENV_PATH" | xargs)
else
  echo "Error: .env file not found at $ENV_PATH"
  exit 1
fi

# Python 실행 명령어
#python main.py -y config/waymo-1137.yaml -p "Add a Benz G in front of me, driving away fast." -s "demo_hkkim"

python main.py -y config/waymo-1137.yaml -p "Create a traffic jam." -s "demo_hkkim"

#python main.py -y config/3dgs-waymo-1137.yaml -p "Add a Benz G in front of me, driving away fast."