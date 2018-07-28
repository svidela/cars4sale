import numpy as np

def outliers_modified_z_score(ys):
    #http://colingorrie.github.io/outlier-detection.html#modified-z-score-method
    threshold = 3.5

    median_y = np.median(ys)
    median_absolute_deviation_y = np.median(np.abs(ys - median_y))
    modified_z_scores = 0.6745 * (ys - median_y) / median_absolute_deviation_y
    return np.abs(modified_z_scores) > threshold

def build_query(**kwargs):
    query = {k: v.replace('_',' ').upper() for k,v in kwargs.items()}
    return query
