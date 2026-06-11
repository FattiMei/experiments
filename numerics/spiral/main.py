import cv2
import sys
import numpy as np
from functools import partial


REFERENCE_FILENAME = 'reference.mp4'
OUTPUT_FILENAME = 'cropped.mp4'


def get_fourcc_code(cap) -> str:
    """
    I use this function so that I use the same encoding
    as the input video
    """
    code = cap.get(cv2.CAP_PROP_FOURCC)

    return int(code).to_bytes(4, byteorder=sys.byteorder).decode()


def apply_pipeline(input_filename: str, output_filename: str, pipeline = extract_roi):
    cap = cv2.VideoCapture(input_filename)
    out = None
    frames_written = 0

    while cap.isOpened():
        success, img = cap.read()
        if not success: break

        frame = pipeline(img)
        if out is None:
            out = cv2.VideoWriter(
                output_filename,
                cv2.VideoWriter_fourcc(*get_fourcc_code(cap)),
                cap.get(cv2.CAP_PROP_FPS),
                (
                    roi.shape[1], # the width of the image
                    roi.shape[0]  # the height of the image (number of rows of ndarray)
                )
            )
        else:
            out.write(frame)
            frames_written += 1

    print(f'Total frames written: {frames_written}')

    cap.release()
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
    apply_pipeline(
        REFERENCE_FILENAME,
        "points.mp4",
        partial(extract_points, threshold=50)
    )

