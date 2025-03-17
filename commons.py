import numpy as np

def hexToRgb(hexColor):
    return np.array([int(hexColor[i:i+2], 16) for i in (1, 3, 5)])

def matchWithColor(pixel, hexColor, threshold=40):
    return np.all(np.abs(pixel - hexToRgb(hexColor)) <= threshold)

def matchWithColorM(img, x, y, hexColor, threshold=20):
    targetColor = hexToRgb(hexColor)
    
    offsets = np.array([(0, 0), (-5, 0), (5, 0), (0, -5), (0, 5), (-5, -5), (-5, 5), (5, -5), (5, 5)])

    coords = offsets + np.array([y, x])
    valid_mask = (coords[:, 0] >= 0) & (coords[:, 0] < img.shape[0]) & (coords[:, 1] >= 0) & (coords[:, 1] < img.shape[1])
    
    valid_coords = coords[valid_mask] 

    pixels = img[valid_coords[:, 0], valid_coords[:, 1]]

    return np.any(np.linalg.norm(pixels - targetColor, axis=1) <= threshold)
