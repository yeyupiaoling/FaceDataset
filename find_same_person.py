import os
import time
import json
import shutil
from aip import AipFace
import base64
from tqdm import tqdm
import key_value

client = AipFace(key_value.APP_ID, key_value.API_KEY, key_value.SECRET_KEY)


# 把图片转换成base64
def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return base64.b64encode(fp.read()).decode()


# 调用接口预测两人脸，其中第一个人脸是正确的人脸
def match_image(main_image, image2):
    data = [
        {
            'image': main_image,
            'image_type': 'BASE64',
        },
        {
            'image': image2,
            'image_type': 'BASE64',
        }
    ]
    try:
        result = client.match(data)
        return result
    except:
        s = '{"msg":"network error"}'
        return json.dumps(s)


# 判断是否为同一个人
def if_same_person(result):
    try:
        score = result['result']['score']
        if score >= 80:
            return True
        else:
            return False
    except:
        return False


# 寻找同一个人的作为0.jpg，作为主的参考图片
def find_same_person(person_image_path):
    # 获取该人中的所有图片
    image_paths = os.listdir(person_image_path)
    if '0.jpg' in image_paths:
        image_paths.remove('0.jpg')
    # 临时选择第一个作为主图片
    temp_image = os.path.join(person_image_path, image_paths[0])
    main_path = os.path.join(person_image_path, '0.jpg')
    if os.path.exists(main_path):
        os.remove(main_path)
    shutil.copyfile(temp_image, main_path)
    for main_image in image_paths:
        # 获取主图片的全路径
        main_image = os.path.join(person_image_path, main_image)
        # 获取主图片的base64
        main_img = get_file_content(main_image)
        # 统计相同人脸数量
        same_sum = 0
        for other_image in image_paths:
            # 获取其他对比人脸的全路径
            other_image = os.path.join(person_image_path, other_image)
            # 获取其他对比图片的base64
            other_img = get_file_content(other_image)
            # 获取对比结果
            result = match_image(main_img, other_img)
            time.sleep(0.5)
            # 判断是不是同一个人
            if if_same_person(result):
                same_sum += 1
            # 当相同的人脸超过6个是就做为主图片
            if same_sum >= 6:
                if os.path.exists(main_path):
                    os.remove(main_path)
                shutil.copyfile(main_image, main_path)
                break
        if same_sum > 6:
            break


if __name__ == '__main__':
    father_path = 'star_image_processed/'
    name_paths = os.listdir(father_path)
    print('开始提取的主图片')
    for name_path in tqdm(name_paths):
        # 开始判断各个人脸
        name_path = os.path.join(father_path, name_path)
        find_same_person(name_path)
    print("提取完成")