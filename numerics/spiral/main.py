import cv2
import sys
import numpy as np
import itertools
from functools import partial


REFERENCE_FILENAME = 'reference.mp4'
OUTPUT_FILENAME = 'cropped.mp4'


def read_from_video(filename: str) -> list[np.ndarray]:
    res = []
    cap = cv2.VideoCapture(filename)

    while cap.isOpened():
        success, img = cap.read()

        if not success: break
        else: res.append(img)

    cap.release()
    return res


def write_to_video(frames, filename: str, fps: int = 30):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    reference = next(frames)
    fwidth = reference.shape[1]
    fheight = reference.shape[0]
    out = cv2.VideoWriter(
        filename,
        fourcc,
        fps,
        (reference.shape[1], # the width of the frame
         reference.shape[0]) # the height of the frame (the number of rows of ndarray)
    )

    frames_written = 0
    for frame in itertools.chain([reference], frames):
        assert(frame.shape == reference.shape)
        out.write(frame)

        frames_written += 1

    print(f'Total frames written: {frames_written}')
    out.release()


def extract_roi(img: np.ndarray):
    # these are hardcoded constants for extracting the ROI
    UPPER_LEFT = (48,88)
    LOWER_RIGHT = (303, 360)

    # the first dimension is the number of rows
    return img[
        UPPER_LEFT[1]:LOWER_RIGHT[1],
        UPPER_LEFT[0]:LOWER_RIGHT[0],
    ]


def extract_points(img: np.ndarray, threshold: int) -> np.ndarray:
    roi = extract_roi(img)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    binary_mask = gray < threshold
    gray = np.array(255*binary_mask, dtype=np.uint8)

    return np.array([gray]*3).transpose(1,2,0)


if __name__ == '__main__':
    frames = read_from_video(REFERENCE_FILENAME)

    write_to_video(map(extract_roi, frames), 'roi.mp4')
    write_to_video(map(partial(extract_points, threshold=50), frames), 'points.mp4')

