#!/bin/bash

# Define the start and end patterns for sed
START_PATTERN="fun SkeletonLoader("
END_PATTERN="fun FloatingDownloadProgress("

# Use sed to replace the SkeletonLoader function
sed -i "/$START_PATTERN/,/$END_PATTERN/{
  /$START_PATTERN/!{
    /$END_PATTERN/!d
  }
  /$START_PATTERN/r skeleton_loader.kt
  /$START_PATTERN/d
}" app/src/main/java/com/auradownloader/app/MainActivity.kt

