import imghdr
import os
import numpy
from PIL import Image
from tqdm import tqdm


# 删除不是JPEG或者PNG格式的图片
def delete_error_image(father_path):
    # 获取父级目录的所有文件以及文件夹
    image_paths = []
    for root, dirs, files in os.walk(father_path):
        for file in files:
            image_paths.append(os.path.join(root, file))
    for image in tqdm(image_paths):
        try:
            # 获取图片的类型
            image_type = imghdr.what(image)
            # 如果图片格式不是JPEG同时也不是PNG就删除图片
            if image_type is not 'jpeg' and image_type is not 'png':
                os.remove(image)
                continue
            # 删除灰度图
            img = numpy.array(Image.open(image))
            if len(img.shape) is 2:
                os.remove(image)
        except:
            os.remove(image)


if __name__ == '__main__':
    print('开始删除错误图片')
    delete_error_image('star_image/')
    print("删除完成")