import cv2
import os
import numpy as np


def convert_images_to_video(image_folder, video_name, fps=30):
    """
    Convert a sequence of images to a video.

    Parameters:
    - image_folder: Path to the folder containing images.
    - video_name: Output video file name.
    - fps: Frames per second for the output video.
    """
    images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]

    # Sort the images by name
    images.sort(key=lambda x: int(x.split(".")[0]))

    # Determine the width and height from the first image
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Be sure to use lower case
    out = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

    for image in images:
        img = cv2.imread(os.path.join(image_folder, image))
        out.write(img)  # Write out frame to video

    out.release()


for i in range(1, 24):
    image_folder = f"/home/pirate/Downloads/positive_cropped/seq{i}/images"
    video_name = f"src/polyp_ui/examples/{i}.mp4"
    fps = 5  # Frames per second

    convert_images_to_video(image_folder, video_name, fps)
