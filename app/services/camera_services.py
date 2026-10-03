"""
Phase 3 - Camera & Document Scanner Service
Handles 4-corner paper contour detection and perspective warping.
"""
import cv2
import numpy as np


def order_points(pts: np.ndarray) -> np.ndarray:
  """Orders 4 points: [top-left, top-right, bottom-right, bottom-left]"""
  rect = np.zeros((4, 2), dtype="float32")
  s = pts.sum(axis=1)
  rect[0] = pts[np.argmin(s)]  # top-left
  rect[2] = pts[np.argmax(s)]  # bottom-right

  diff = np.diff(pts, axis=1)
  rect[1] = pts[np.argmin(diff)]  # top-right
  rect[3] = pts[np.argmax(diff)]  # bottom-left
  return rect


def four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
  """Applies Bird's Eye View perspective warp on a 4-point polygon contour."""
  rect = order_points(pts)
  (tl, tr, br, bl) = rect

  # Compute width of new warped image
  width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
  width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
  max_width = max(int(width_a), int(width_b))

  # Compute height of new warped image
  height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
  height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
  max_height = max(int(height_a), int(height_b))

  dst = np.array(
      [
          [0, 0],
          [max_width - 1, 0],
          [max_width - 1, max_height - 1],
          [0, max_height - 1],
      ],
      dtype="float32",
  )

  matrix = cv2.getPerspectiveTransform(rect, dst)
  warped = cv2.warpPerspective(image, matrix, (max_width, max_height))
  return warped


def detect_paper_and_warp(image: np.ndarray):
  """Finds the largest 4-sided contour (paper) and warps it.

  Falls back to the original image if no quadrilateral is found.
  """
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  blurred = cv2.GaussianBlur(gray, (5, 5), 0)
  canny = cv2.Canny(blurred, 50, 150)

  contours, _ = cv2.findContours(
      canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
  )

  max_area = 0
  paper_corners = None

  for cnt in contours:
    area = cv2.contourArea(cnt)
    if area > 5000:  # Noise threshold
      peri = cv2.arcLength(cnt, True)
      approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

      if len(approx) == 4 and area > max_area:
        max_area = area
        paper_corners = approx.reshape(4, 2)

  if paper_corners is not None:
    warped = four_point_transform(image, paper_corners)
    return warped, True

  return image, False