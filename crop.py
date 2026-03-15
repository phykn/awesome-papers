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
    v_clusters = get_clusters(binary, 1, gap=15) # Tighter gap to separate lines
    if not v_clusters: return
    
    # Calculate density for each cluster
    cluster_stats = []
    for s, e in v_clusters:
        height = e - s
        ink_count = np.sum(binary[s:e, :])
        density = ink_count / (height * w)
        cluster_stats.append({'range': (s, e), 'height': height, 'density': density, 'ink': ink_count})

    # The diagram is almost always the cluster with the most total ink
    main_idx = np.argmax([c['ink'] for c in cluster_stats])
    main_s, main_e = cluster_stats[main_idx]['range']
    
    # We want to keep clusters that are "part" of the diagram 
    # and remove those that are "separate" (captions, page text).
    # Rule: Keep clusters that have high ink and are near the main cluster.
    # Discard clusters at edges if they are separated by a large gap or are sparse.
    
    final_v_clusters = [cluster_stats[main_idx]['range']]
    
    # Search upwards from main
    for i in range(main_idx - 1, -1, -1):
        s, e = cluster_stats[i]['range']
        gap = v_clusters[i+1][0] - e
        # If gap is small (e.g. labels), or cluster is very dense, keep it.
        # If gap is large (standard line spacing of text), stop.
        if gap < 40 or cluster_stats[i]['density'] > 0.3:
            final_v_clusters.append((s, e))
        else:
            break
            
    # Search downwards from main
    for i in range(main_idx + 1, len(v_clusters)):
        s, e = cluster_stats[i]['range']
        gap = s - v_clusters[i-1][1]
        if gap < 40 or cluster_stats[i]['density'] > 0.3:
            final_v_clusters.append((s, e))
        else:
            break

    ymin = min(c[0] for c in final_v_clusters)
    ymax = max(c[1] for c in final_v_clusters)
    
    # Horizontal analysis within the new ymin:ymax
    h_clusters = get_clusters(binary[ymin:ymax, :], 0, gap=20)
    if not h_clusters: return

    # Similarly, find main horizontal cluster
    h_ink = [np.sum(binary[ymin:ymax, s:e]) for s, e in h_clusters]
    main_h_idx = np.argmax(h_ink)
    
    final_h_clusters = [h_clusters[main_h_idx]]
    
    # Expand horizontally if gaps are small
    for i in range(main_h_idx - 1, -1, -1):
        if h_clusters[i+1][0] - h_clusters[i][1] < 50:
            final_h_clusters.append(h_clusters[i])
        else: break
    for i in range(main_h_idx + 1, len(h_clusters)):
        if h_clusters[i][0] - h_clusters[i-1][1] < 50:
            final_h_clusters.append(h_clusters[i])
        else: break

    xmin = min(c[0] for c in final_h_clusters)
    xmax = max(c[1] for c in final_h_clusters)

    pad = 10
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
