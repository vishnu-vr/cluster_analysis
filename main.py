# import sys
# sys.path.insert(1, '../')
from services.clean import CleanService
import utils.utils as utils
import models.file_model as file_model
import models.config as Config
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import os
import shutil
from sklearn.decomposition import TruncatedSVD
import sys
from matplotlib import pyplot
from numpy import where
from numpy import unique
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt

def clean(dataset_location: str, config: Config.Config) -> list[file_model.FileModel]:
    clean = CleanService(dataset_location)
    
    files = clean.get_file_models()

    pre_processed_file_objects = files[0]
    failed_files = files[1]

    utils.save_to_disk(pre_processed_file_objects, config.preprocessed_object_location)
    utils.save_to_disk(failed_files, config.error_files)

    return pre_processed_file_objects

def vectorize_documents(clean_file_models :list[file_model.FileModel]):
    corpus: list[str] = []

    for file in clean_file_models:
        corpus.append(file.json_content)

    vectorizer = TfidfVectorizer()
    return vectorizer.fit_transform(corpus), vectorizer


def get_preprocessed_files(config: Config.Config) -> list[file_model.FileModel]:
    _clean_file_models: list[file_model.FileModel] = []
    if (len(config.preprocessed_object_location) > 0):
        _clean_file_models: list[file_model.FileModel] = utils.restore_from_disk(config.preprocessed_object_location)
    else:
        _clean_file_models: list[file_model.FileModel] = clean(config.dataset_location)

    return _clean_file_models

def remove_files_with_null_content(clean_file_models: list[file_model.FileModel], mappings):
    clean_file_models_without_null_content: list[file_model.FileModel] = []
    for clean_file in clean_file_models:
        if clean_file.json_content is None:
            mappings["discarded_files"].append(clean_file.location)
            continue

        clean_file_models_without_null_content.append(clean_file)
    return clean_file_models_without_null_content

def cluster_with_kmeans(dim_red_features, num_of_clusters: int):
    model = KMeans(n_clusters=num_of_clusters)
    model.fit(dim_red_features)
    yhat = model.predict(dim_red_features)
    return yhat

def map_file_locations_with_clusters(mappings, clean_file_models_without_null_content, yhat):
    for index, cluster_num in enumerate(yhat):
        if (not cluster_num in mappings): mappings[cluster_num] = []
        mappings[cluster_num].append(clean_file_models_without_null_content[index].location)

def save_clusters_on_disk(mappings, config: Config.Config):
    for cluster in mappings.keys():
        os.mkdir(os.path.join(config.result_location, str(cluster)))

    for cluster, file_locs in mappings.items():
        for file_loc in file_locs:
            src = os.path.join(config.dataset_location, str(file_loc))
            dest = os.path.join(config.result_location, str(cluster), file_loc)

            shutil.copyfile(src, dest)

def plot(config: Config.Config):
    features = utils.restore_from_disk(config.feature_location)
    yhat = utils.restore_from_disk(config.cluster_location)

    clusters = unique(yhat)
    fig = plt.figure(figsize = (10, 7))
    ax = plt.axes(projection ="3d")

    # create scatter plot for samples from each cluster
    for cluster in clusters:
        print(cluster)
        # get row indexes for samples with this cluster
        row_ix = where(yhat == cluster)

        x = features[row_ix, 0]
        y = features[row_ix, 1]
        z = features[row_ix, 2]

        ax.scatter3D(x, y, z)
    plt.legend(clusters.tolist())
    plt.show()

if __name__ == "__main__":

    config = Config.Config("config.json")

    clean_file_models: list[file_model.FileModel] = get_preprocessed_files(config=config)

    mappings = {}
    mappings["discarded_files"] = []
    clean_file_models_without_null_content = remove_files_with_null_content(clean_file_models, mappings)

    print("vectorizing docs", end="\n")
    feature, vectorizer = vectorize_documents(clean_file_models_without_null_content)

    print("Reduce Dimensions", end="\n")
    svd = TruncatedSVD(n_components=5, n_iter=7, random_state=42)
    dim_red_features = svd.fit_transform(feature)

    print("clustering", end="\n")
    yhat = cluster_with_kmeans(dim_red_features, num_of_clusters=config.num_of_clusters)

    print("saving results", end="\n")
    map_file_locations_with_clusters(mappings, clean_file_models_without_null_content, yhat)

    utils.save_to_disk(dim_red_features, config.feature_location)
    utils.save_to_disk(yhat, config.cluster_location)
    utils.save_to_disk(mappings, config.files_to_cluster_mapping_location)

    print("sorting files", end="\n")
    # create folders for each cluster
    save_clusters_on_disk(mappings, config)