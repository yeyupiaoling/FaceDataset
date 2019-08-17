import os
import shutil

import face_recognition
import numpy


# 寻找同一个人的作为0.jpg，作为主的参考图片
def find_same_person(person_image_path):
    # 获取该人中的所有图片
    image_paths = os.listdir(person_image_path)
    known_face_encodings = []
    for image_path in image_paths:
        img_path = os.path.join(person_image_path, image_path)
        try:
            image = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(image, num_jitters=10)[0]
            known_face_encodings.append(encodings)
        except Exception as e:
            try:
                os.remove(img_path)
            except Exception as e:
                print(e)

    for image_path in image_paths:
        try:
            print(image_path)
            img_path = os.path.join(person_image_path, image_path)
            image = face_recognition.load_image_file(img_path)
            a_single_unknown_face_encoding = face_recognition.face_encodings(image, num_jitters=10)[0]
            results = face_recognition.compare_faces(known_face_encodings, a_single_unknown_face_encoding,
                                                     tolerance=0.5)
            results = numpy.array(results).astype(numpy.int64)
            if numpy.sum(results) > 5:
                main_path = os.path.join(person_image_path, '0.jpg')
                if os.path.exists(main_path):
                    os.remove(main_path)
                shutil.copyfile(img_path, main_path)
                break
        except:
            pass


if __name__ == '__main__':
    father_path = 'star_image_processed/'
    name_paths = os.listdir(father_path)
    for name_path in name_paths:
        print('已开始提取 %s 的主图片' % name_path)
        # 开始判断各个人脸
        name_path = os.path.join(father_path, name_path)
        image_paths = os.listdir(name_path)
        if '0.jpg' in image_paths:
            continue
        find_same_person(name_path)
