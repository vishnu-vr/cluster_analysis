class FileModel:
    def __init__(self, filename: str, json_content: str, location: str) -> None:
        self.filename = filename
        self.json_content = json_content
        self.location = location