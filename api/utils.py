import numpy as np

#
# Outliers detection function from:
# http://colingorrie.github.io/outlier-detection.html
#
def outliers_modified_z_score(ys):
    threshold = 3.5

    median_y = np.median(ys)
    median_absolute_deviation_y = np.median(np.abs(ys - median_y))
    modified_z_scores = 0.6745 * (ys - median_y) / median_absolute_deviation_y
    return np.abs(modified_z_scores) > threshold

def outliers_iqr(ys):
    quartile_1, quartile_3 = np.percentile(ys, [25, 75])
    iqr = quartile_3 - quartile_1
    lower_bound = quartile_1 - (iqr * 1.5)
    upper_bound = quartile_3 + (iqr * 1.5)
    return (ys > upper_bound) | (ys < lower_bound)


def build_query(**kwargs):
    query = {k: v.replace('_',' ').upper() for k,v in kwargs.items()}
    return query
