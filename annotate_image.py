import os
import shutil
import time
from aip import AipFace
import base64
import json
from tqdm import tqdm

# 百度人脸识别的 APP_ID, API_KEY, SECRET_KEY
APP_ID = ''
API_KEY = ''
SECRET_KEY = ''
client = AipFace(APP_ID, API_KEY, SECRET_KEY)

# 存放人的名字
names = set()

dict_names_list = []

# 把图片转换成base64
def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return base64.b64encode(fp.read()).decode()


# 预测图片
def detect_image(image):
    options = {}
    options["max_face_num"] = 1
    options["face_field"] = 'beauty,expression,faceshape,gender,glasses,landmark,landmark72,landmark150,age'
    try:
        result = client.detect(image, image_type='BASE64', options=options)
        return result
    except:
        s = '{"msg":"network error"}'
        return json.dumps(s)


# 把预测结果和图片的URL写入到标注文件中
def annotate_image(result, image_path, image_url):
    # 获取文件夹名字，并得到已经记录多少人
    father_path = os.path.dirname(image_path)
    image_name = os.path.basename(image_path).split('.')[0]
    # 获取明星的名字
    name = father_path.split('/')[-1]
    # 把这些名字转换成数字标号
    names.add(name)
    num_name = str(len(names) - 1)
    img_path = num_name + '/' + os.path.basename(image_path)
    annotation_path = os.path.join('annotations', num_name)
    dict_names_list.append((name, num_name))
    annotation_file_path = os.path.join(annotation_path, str(image_name) + '.json')
    # 创建存放标注文件的文件夹
    if not os.path.exists(annotation_path):
        os.makedirs(annotation_path)

    try:
        # 名字
        name = name
        # 年龄
        age = result['result']['face_list'][0]['age']
        # 性别，male:男性 female:女性
        gender = result['result']['face_list'][0]['gender']['type']
        # 脸型，square: 正方形 triangle:三角形 oval: 椭圆 heart: 心形 round: 圆形
        face_shape = result['result']['face_list'][0]['face_shape']['type']
        # 是否带眼镜，none:无眼镜，common:普通眼镜，sun:墨镜
        glasses = result['result']['face_list'][0]['glasses']['type']
        # 表情，none:不笑；smile:微笑；laugh:大笑
        expression = result['result']['face_list'][0]['expression']['type']
        # 颜值，范围0-100
        beauty = result['result']['face_list'][0]['beauty']
        # 人脸在图片中的位置
        location = str(result['result']['face_list'][0]['location']).replace("'", '"')
        # 人脸旋转角度参数
        angle = str(result['result']['face_list'][0]['angle']).replace("'", '"')
        # 72个特征点位置
        landmark72 = str(result['result']['face_list'][0]['landmark72']).replace("'", '"')
        # 150个特征点位置
        landmark150 = str(result['result']['face_list'][0]['landmark150']).replace("'", '"')
        # 4个关键点位置，左眼中心、右眼中心、鼻尖、嘴中心
        landmark = str(result['result']['face_list'][0]['landmark']).replace("'", '"')
        # 拼接成符合json格式的字符串
        txt = '{"name":"%s", "image_path":"%s", "image_url":"%s","age":%f, "gender":"%s", "glasses":"%s", "expression":"%s", "beauty":%f, "face_shape":"%s", "location":%s, "angle":%s, "landmark72":%s, "landmark150":%s, "landmark":%s}' \
              % (name, img_path, image_url, age, gender, glasses, expression, beauty, face_shape, location, angle,
                 landmark72, landmark150, landmark)
        # 转换成json数据并格式化
        json_dicts = json.loads(txt)
        json_format = json.dumps(json_dicts, sort_keys=True, indent=4, separators=(',', ':'))
        # 写入标注文件
        with open(annotation_file_path, 'w', encoding='utf-8') as f_a:
            f_a.write(json_format)

        # 移动已标注的图片文件
        save_path = os.path.join('images/', num_name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        shutil.move(image_path, os.path.join('images/', img_path))
    except Exception as e:
        print(e)


if __name__ == '__main__':
    list_path = 'image_url_list.txt'
    with open(list_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # 开始标记
    for line in tqdm(lines):
        image_path, image_url = line.split('\t')
        image_url = image_url.replace('\n', '')
        if not os.path.exists(image_path):
            continue
        img = get_file_content(image_path)
        # 预测图片并写入标注信息
        result = detect_image(img)
        annotate_image(result, image_path, image_url)
        time.sleep(0.3)

    print('标记完成')
