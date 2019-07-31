import os
import shutil
import face_recognition


# 删除两个人脸以上的图片或者没有人脸的图片
def delete_image(image_path):
    try:
        image = face_recognition.load_image_file(image_path)
        result = face_recognition.face_locations(image, model='cnn')
        if len(result) != 1:
            os.remove(image_path)
    except:
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
