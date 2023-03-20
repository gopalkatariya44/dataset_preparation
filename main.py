import argparse

from models import Dataset

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--images', type=str,
                        default=None, help='images path')
    parser.add_argument('-l', '--labels', type=str,
                        default=None, help='Yolo txt annotations path')
    parser.add_argument('-c', '--classes', type=str,
                        default=None, help='classes.txt path')
    parser.add_argument('-csv', '--csv-output', type=str,
                        default=None, help='csv output path')
    parser.add_argument('-o', '--output', type=str,
                        default='sprate_labels', help='labels output path')

    opt = parser.parse_args()
    if opt.labels is None:
        opt.labels = opt.images.split('/images')[0] + "/labels"
        print(opt.labels)

    if opt.csv_output is None:
        opt.csv_output = opt.images.split('/images')[0] + '/dataset.csv'

    if opt.classes is None:
        opt.classes = opt.labels + "/classes.txt"

    dataset = Dataset(labels_path=opt.labels,
                      images_path=opt.images,
                      classes_path=opt.classes)

    print(dataset.__dict__)

    # dataset.to_csv(opt.csv_output)

    dataset.sprate_labels(opt.output)

    # dataset.change_label_to_index(opt.output)
