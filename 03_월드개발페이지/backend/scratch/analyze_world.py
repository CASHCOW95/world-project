import cv2
import os

path = r"c:\Users\ydh24\Desktop\밋업\python\assets\result.png"
if os.path.exists(path):
    img = cv2.imread(path)
    if img is not None:
        print(f"Result Shape: {img.shape}")
    else:
        print("Failed to read image")
else:
    print("File not found")
