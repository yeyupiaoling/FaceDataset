import os
import shutil
import json
import time
from aip import AipFace
import base64
import key_value
from tqdm import tqdm

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


# 删除不是同一个的图片
def delete_image(result, image_path):
    try:
        score = result['result']['score']
        if score < 80:
            os.remove(image_path)
    except:
        os.remove(image_path)


# 判断是否以及标记正确类别的图片
def check_if_all_rename(father_path, name_paths):
    exist = True
    for name_path in name_paths:
        main_image = os.path.join(father_path, name_path, '0.jpg')
        if not os.path.exists(main_image):
            exist = False
            print('%s 还没标记`0.jpg`图片' % name_path)
    return exist


if __name__ == '__main__':
    father_path = 'star_image_processed/'
    name_paths = os.listdir(father_path)
    # 确保全部文件夹都下的图片都标记了
    print('正在对比图片')
    if check_if_all_rename(father_path, name_paths):
        for name_path in tqdm(name_paths):
            image_paths = os.listdir(os.path.join(father_path, name_path))
            for image_path in image_paths:
                # 正确图片的路径
                main_image = os.path.join(father_path, name_path, '0.jpg')
                # 要对比的图片
                img_path = os.path.join(father_path, name_path, image_path)
                # 获取图片的base64
                main_img = get_file_content(main_image)
                img = get_file_content(img_path)
                time.sleep(0.5)
                # 预测图片并进行处理
                result = match_image(main_img, img)
                delete_image(result, img_path)
            shutil.move(src=os.path.join(father_path, name_path), dst=os.path.join('star_image', name_path))
        print('对比完成')
    else:
        print('请标记完成`0.jpg`图片，再重新执行')