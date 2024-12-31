#!/bin/bash

# chmod +x link_tfrecords.sh
# bash link_tfrecords.sh

# Source and target directories
#SRC_DIR="/home/hyunkoo/DATA/NAS/nfsRoot/Datasets/Waymo_Datasets/Perception_Dataset_v1_4_3_with_maps/training"
SRC_DIR="/home/hyunkoo/DATA/NAS/nfsRoot/Datasets/Waymo_Datasets/Perception_Dataset_v1_4_3_with_maps/validation"

#DEST_DIR="/home/hyunkoo/DATA/HDD8TB/Add_Objects_DrivingScense/ChatSim/data/waymo_tfrecords/1.4.2"
DEST_DIR="/home/hyunkoo/DATA/ssd8tb/Journal/ChatSim/data/waymo_tfrecords/1.4.2"

# Create the destination directory if it does not exist
mkdir -p "$DEST_DIR"

# Find all .tfrecord files in the source directory and create symbolic links in the destination directory
find "$SRC_DIR" -type f -name "*.tfrecord" | while read -r file; do
    ln -s "$file" "$DEST_DIR/$(basename "$file")"
done

# Print completion message
echo "Symbolic links created for all .tfrecord files from $SRC_DIR to $DEST_DIR."
