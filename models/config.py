import json

class Config:
    def __init__(self, config_loc: str) -> None:
        config = json.load(open(config_loc))
        self.dataset_location: str = config["dataset_location"]
        self.preprocessed_object_location: str = config["preprocessed_object_location"]
        self.result_location: str = config["result_location"]
        self.error_files: str = config["error_files"]
        self.feature_location: str = config["feature_location"]
        self.cluster_location: str = config["cluster_location"]
        self.files_to_cluster_mapping_location: str = config["files_to_cluster_mapping_location"]
        self.num_of_clusters: int = int(config["num_of_clusters"])