import os
import re
import pandas as pd
from .dataset_schema import DatasetSchema
import shutil
from PIL import Image

IMAGE_REGEX = "([^\\s]+(\\.(?i)(jpe?g|png|gif|bmp))$)"


def convert_cor_to_yolo_txt(label, x_min, y_min, x_max, y_max, image):
    img = Image.open(image)
    dw = 1. / img.width
    dh = 1. / img.height
    x = (x_min + x_max) / 2.0 - 1
    y = (y_min + y_max) / 2.0 - 1
    w = x_max - x_min
    h = y_max - y_min
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return f"{label} {x} {y} {w} {h}\n"


class Dataset:
    def __init__(self, labels_path: str = None, images_path: str = None, classes_path: str = None):
        """
        labels_path: add yolo txt folder path here.\n
        images_path: add yolo images folder path here.\n
        classes_path: add single file classes.txt here.
        """

        self.labels_path = labels_path
        self.images_path = images_path
        self.classes_path = classes_path

        if self.labels_path is None:
            self.labels_path = images_path
        elif self.images_path is None:
            self.images_path = labels_path
        elif self.labels_path is None and self.images_path is None:
            print("please give dataset paths....")
        elif self.classes_path is None:
            print("please give classes paths....")

    @staticmethod
    def verfy_dataset():
        print("Verfy Dataset.........")

    def read_classes(self):
        """
        txt format:\n
        bus\n
        car\n
        bike\n
        :return: List Classes ["bus", "car", "bike"]
        """
        try:
            with open(self.classes_path, 'r') as f:
                return [i.split('\n')[0].strip() for i in f.readlines()]
        except Exception as e:
            print(e)

    def to_csv(self, csv_path=None):
        try:
            df = pd.DataFrame(self.dataset_to_list())
            df.to_csv(csv_path, index=False)
            print(f"csv file generated here '{csv_path}'")
        except Exception as e:
            print(e)

    def similar_image_text_dict(self):
        try:
            compiled_image_regex = re.compile(IMAGE_REGEX)
            images_list = [i for i in os.listdir(self.images_path) if re.search(compiled_image_regex, i)]
            yolo_txt_list = [i for i in os.listdir(self.labels_path) if i.endswith('.txt') and i != "classes.txt"]
            # create dict for same txt and images
            file_dict = {}
            for txt in yolo_txt_list:
                for image in images_list:
                    prefix = txt[:-4:]

                    if (f"{prefix}.jpg" == image or
                            f"{prefix}.png" == image or
                            f"{prefix}.jpeg" == image):
                        file_dict[prefix] = [image, txt]
            return file_dict
        except Exception as e:
            print(e)

    def dataset_to_list(self):
        """
        return all images path and txt path with their labels\n
        {
        \t'index': 0,\n
        \t'image_path': 'dataset/images/20230207145026.jpg',\n
        \t'txt_path': 'dataset/annotations/20230207145026.txt',\n
        \t'classes': {'0': 'car'}\n
        }
        :return: list of dict
        """
        dataset_list = []
        # now start create a dataset list for csv
        final_dict = self.similar_image_text_dict()
        try:
            for index, i in enumerate(final_dict):
                with open(f"{self.labels_path}/{final_dict[i][-1]}", 'r') as f:
                    lines = f.readlines()
                dataset_schema = DatasetSchema(index=index,
                                               image_path=f"{self.images_path}/{final_dict[i][0]}",
                                               txt_path=f"{self.labels_path}/{final_dict[i][1]}",
                                               classes={},
                                               )
                for line in lines:
                    label_index = int(line.split()[0])
                    classes_list = self.read_classes()
                    dataset_schema.classes.update({
                        f"{label_index}": classes_list[label_index]
                    })
                dataset_list.append(dataset_schema.as_dict())
            return dataset_list
        except Exception as e:
            print(e)

    def sprate_labels(self, output_path: str):
        classes = self.read_classes()
        final_dict = self.similar_image_text_dict()
        try:
            print('sprate labels started...')
            for i in final_dict:
                with open(f"{self.labels_path}/{final_dict[i][-1]}", 'r') as f:
                    lines = f.readlines()
                if len(lines) == 0:
                    # print("no annotations available..")
                    os.makedirs(f"{output_path}/raw_images", exist_ok=True)
                    true_image = f"{output_path}/raw_images/{final_dict[i][0]}"
                    if not os.path.exists(f"{output_path}/raw_images/{final_dict[i][0]}"):
                        shutil.copy(self.images_path + '/' + final_dict[i][0], true_image)
                else:
                    for line in lines:
                        label_index = int(line.split()[0])

                        # sprate clss dir structure
                        labels_path = f"{output_path}/{classes[label_index]}/labels"
                        images_path = f"{output_path}/{classes[label_index]}/images"

                        # make dirs
                        os.makedirs(f"{labels_path}", exist_ok=True)
                        os.makedirs(f"{images_path}", exist_ok=True)

                        # make classes.txt
                        classes_txt = f"{labels_path}/classes.txt"
                        if not os.path.exists(classes_txt):
                            with open(classes_txt, 'a') as f:
                                f.write(classes[label_index])

                        # write txt
                        with open(f"{labels_path}/{final_dict[i][1]}", 'a') as f:
                            f.write(line.replace(str(label_index), "0", 1))
                        image = f"{images_path}/{final_dict[i][0]}"

                        # copy image
                        if not os.path.exists(image):
                            shutil.copy(self.images_path + '/' + final_dict[i][0], image)

        except Exception as e:
            print(e)
        print(f"sprate labels folder generated here : {output_path}/")

    def change_label_to_index(self, output_path: str):
        classes = self.read_classes()
        final_dict = self.similar_image_text_dict()

        try:
            for i in final_dict:
                with open(f"{self.labels_path}/{final_dict[i][-1]}", 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    line_split = line.split()
                    label = line.split()[0]
                    label_index = 0
                    for inx, cls in enumerate(classes):
                        if cls == label:
                            label_index = inx
                            break
                    print("1-->", label_index, line_split[1], line_split[2], line_split[3], line_split[4])
                    yolo_txt = convert_cor_to_yolo_txt(label_index, float(line_split[1]), float(line_split[2]),
                                                       float(line_split[3]),
                                                       float(line_split[4]), self.images_path + '/' + final_dict[i][0])
                    print("2-->", yolo_txt)
                    os.makedirs(f"{output_path}", exist_ok=True)
                    with open(f"{output_path}/{final_dict[i][1]}", 'a') as f:
                        f.write(yolo_txt)
                    if not os.path.exists(output_path + '/' + final_dict[i][0]):
                        shutil.copy(self.images_path + '/' + final_dict[i][0],
                                    output_path + '/' + final_dict[i][0])
            print("label changed done.")
        except Exception as e:
            print(e)

    def xml_to_yolo(self):
        pass
