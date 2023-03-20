class DatasetSchema:
    def __init__(self, index: int, image_path: str, txt_path: str, classes: dict):
        self.index = index
        self.image_path = image_path
        self.txt_path = txt_path
        self.classes = classes

    def as_dict(self):
        return {
            "index": self.index,
            "image_path": self.image_path,
            "txt_path": self.txt_path,
            "classes": self.classes
        }
