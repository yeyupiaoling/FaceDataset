import os
import shutil
import cv2
import numpy as np
from mtcnn.mtcnn import MTCNN

detector = MTCNN()


# 删除两个人脸以上的图片或者没有人脸的图片
def delete_image(image_path):
    try:
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)
        result = detector.detect_faces(img)
        if len(result) != 1:
            os.remove(image_path)
        else:
            confidence = result[0]['confidence']
            if confidence < 0.85:
                os.remove(image_path)
    except Exception as e:
        print(e)
        print('delete: %s' % image_path)
        os.remove(image_path)


if __name__ == '__main__':
    father_path = 'star_image'
    processed_path = 'star_image_processed'

    try:
        name_paths = os.listdir(father_path)
        for name_path in name_paths:
            print('正在清理 %s 图片...' % name_path)
            image_paths = os.listdir(os.path.join(father_path, name_path))
            for image_path in image_paths:
                # 获取图片路径
                img_path = os.path.join(father_path, name_path, image_path)
                delete_image(img_path)
            shutil.move(src=os.path.join(father_path, name_path), dst=os.path.join(processed_path, name_path))
        print('清理完成')
    except:
        pass
