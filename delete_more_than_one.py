import os
import time
from aip import AipFace
import base64
import json
import shutil
import key_value
from tqdm import tqdm

client = AipFace(key_value.APP_ID, key_value.API_KEY, key_value.SECRET_KEY)


# 把图片转换成base64
def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return base64.b64encode(fp.read()).decode()


# 预测图片
def detect_image(image):
    options = {}
    options["max_face_num"] = 5
    options["face_field"] = 'facetype'
    try:
        result = client.detect(image, image_type='BASE64', options=options)
        return result
    except:
        s = '{"msg":"network error"}'
        return json.dumps(s)


# 删除两个人脸以上的图片或者没有人脸的图片
def delete_image(result, image_path):
    try:
        face_num = int(result['result']['face_num'])
        if face_num is not 1:
            os.remove(image_path)
        else:
            face_type = result['result']['face_list'][0]['face_type']['type']
            probability = result['result']['face_list'][0]['face_type']['probability']
            if face_type == 'cartoon' and probability > 0.8:
                os.remove(image_path)
    except:
        os.remove(image_path)


if __name__ == '__main__':
    father_path = 'star_image'
    processed_path = 'star_image_processed'

    name_paths = os.listdir(father_path)
    print('开始清理图片')
    image_paths = []
    for root, dirs, files in os.walk(father_path):
        for file in files:
            image_paths.append(os.path.join(root, file))
    for img_path in tqdm(image_paths):
        # 获取图片的base64
        img = get_file_content(img_path)
        time.sleep(0.5)
        # 预测图片并进行处理
        result = detect_image(img)
        delete_image(result, img_path)
    for name_path in os.listdir(father_path):
        shutil.move(src=os.path.join(father_path, name_path), dst=os.path.join(processed_path, name_path))
    print('清理完成')