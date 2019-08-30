import os
import shutil

import face_recognition


# 判断是否以及标记正确类别的图片
def check_if_all_rename(father_path, name_paths):
    exist = True
    i = 0
    for name_path in name_paths:
        main_image = os.path.join(father_path, name_path, '0.jpg')
        if not os.path.exists(main_image):
            shutil.rmtree(os.path.join(father_path, name_path))
            i += 1
            print('%s 还没标记`0.jpg`图片' % name_path)
    print(i)
    return exist


if __name__ == '__main__':
    father_path = 'star_image_processed/'
    name_paths = os.listdir(father_path)
    # 确保全部文件夹都下的图片都标记了
    if check_if_all_rename(father_path, name_paths):
        name_paths = os.listdir(father_path)
        for name_path in name_paths:
            print('正在对比 %s 图片...' % name_path)
            image_paths = os.listdir(os.path.join(father_path, name_path))
            # 正确图片的路径
            main_image = os.path.join(father_path, name_path, '0.jpg')
            try:
                main_img = face_recognition.load_image_file(main_image)
                main_encodings = face_recognition.face_encodings(main_img, num_jitters=10)[0]
            except:
                shutil.rmtree(os.path.join(father_path, name_path))
                continue
            for image_path in image_paths:
                # 要对比的图片
                img_path = os.path.join(father_path, name_path, image_path)
                try:
                    image = face_recognition.load_image_file(img_path)
                    unknown_encoding = face_recognition.face_encodings(image, num_jitters=10)[0]
                    results = face_recognition.compare_faces([main_encodings], unknown_encoding, tolerance=0.6)
                    if not results[0]:
                        os.remove(img_path)
                except:
                    os.remove(img_path)
            shutil.move(src=os.path.join(father_path, name_path), dst=os.path.join('star_image', name_path))
        print('对比完成')
    else:
        print('请标记完成`0.jpg`图片，再重新执行')
