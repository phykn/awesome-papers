import os
import glob
from PIL import Image
import numpy as np

def smart_crop(img_path):
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    gray = img.convert("L")
    arr = np.array(gray)
    binary = (arr < 252).astype(np.uint8)
    
    if not np.any(binary): return

    def get_clusters(mask, axis, gap=30):
        sums = np.sum(mask, axis=axis)
        indices = np.where(sums > 2)[0]
        if len(indices) == 0: return []
        clusters = []
        if len(indices) == 0: return []
        start = indices[0]
        for i in range(1, len(indices)):
            if indices[i] - indices[i-1] > gap:
                clusters.append((start, indices[i-1]))
                start = indices[i]
        clusters.append((start, indices[-1]))
        return clusters

    # Initial vertical clusters
    v_clusters = get_clusters(binary, 1, gap=40)
    if not v_clusters: return
    
    # Filter text-like clusters at edges
    diagram_clusters = []
    for s, e in v_clusters:
        height = e - s
        ink_count = np.sum(binary[s:e, :])
        density = ink_count / (height * w)
        
        # Heuristic: Diagrams are either tall or very dense.
        # Text is short and sparse.
        is_text = (height < 80) and (density < 0.1)
        
        # Also, check if it's a "header" or "footer"
        is_edge = (s < h * 0.1) or (e > h * 0.9)
        
        if is_text and is_edge:
            continue
        diagram_clusters.append((s, e))
    
    if not diagram_clusters:
        # Fallback to the largest cluster
        diagram_clusters = [max(v_clusters, key=lambda x: np.sum(binary[x[0]:x[1], :]))]

    ymin = min(c[0] for c in diagram_clusters)
    ymax = max(c[1] for c in diagram_clusters)
    
    # Horizontal analysis within the ymin:ymax
    h_clusters = get_clusters(binary[ymin:ymax, :], 0, gap=40)
    diagram_h_clusters = []
    for s, e in h_clusters:
        width = e - s
        ink_count = np.sum(binary[ymin:ymax, s:e])
        density = ink_count / ((ymax-ymin) * width)
        
        # Sidebars are narrow or sparse at the edges
        is_sidebar = (width < w * 0.15) and (density < 0.1)
        is_edge = (s < w * 0.15) or (e > w * 0.85)
        
        if is_sidebar and is_edge:
            continue
        diagram_h_clusters.append((s, e))
        
    if not diagram_h_clusters:
        diagram_h_clusters = [max(h_clusters, key=lambda x: np.sum(binary[ymin:ymax, x[0]:x[1]]))]

    xmin = min(c[0] for c in diagram_h_clusters)
    xmax = max(c[1] for c in diagram_h_clusters)

    pad = 15
    final_crop = (
        max(0, xmin - pad),
        max(0, ymin - pad),
        min(w, xmax + pad),
        min(h, ymax + pad)
    )
    
    cropped = img.crop(final_crop)
    cropped.save(img_path)
    print(f"Balanced Cropped {img_path}: {w}x{h} -> {cropped.size[0]}x{cropped.size[1]}")

def main():
    image_paths = glob.glob("asset/**/*.png", recursive=True)
    for path in image_paths:
        try:
            smart_crop(path)
        except Exception as e:
            print(f"Error {path}: {e}")

if __name__ == "__main__":
    main()
