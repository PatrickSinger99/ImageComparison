from feature_extraction import get_folder_content_features
from image_comparison import compare_all_images


def compare_images(folder_path, threshold=0.99, include_subfolders=False):
    image_features = get_folder_content_features(folder_path, include_subfolders)
    comparison_results = compare_all_images(image_features, threshold)
    print(comparison_results)


if __name__ == '__main__':
    compare_images(r"C:\Users\sip4abt\Documents\GitHub\ImageComparison\data\raw-img\cat", include_subfolders=True)
