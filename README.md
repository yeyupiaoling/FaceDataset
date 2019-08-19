# FaceDataset
制作亚洲人脸数据集

## 依赖环境
```
pip3 install baidu-aip -i https://mirrors.aliyun.com/pypi/simple/
pip3 install tqdm -i https://mirrors.aliyun.com/pypi/simple/
pip3 install pillow -i https://mirrors.aliyun.com/pypi/simple/
pip3 install tensorflow==1.14.0 -i https://mirrors.aliyun.com/pypi/simple/
pip3 install mtcnn -i https://mirrors.aliyun.com/pypi/simple/
pip3 install opencv-python -i https://mirrors.aliyun.com/pypi/simple/
pip3 install face_recognition -i https://mirrors.aliyun.com/pypi/simple/
```

# 制作人脸数据集
下面我们就介绍如何制作自己的人脸数据集，项目的开源地址：https://github.com/yeyupiaoling/FaceDataset 。该项目可以分为两个阶段，第一阶段是人脸图片的获取和简单的清洗，第二阶段是人脸图片的高级清洗和标注人脸信息。人脸信息的标注和清洗使用到了百度的人脸识别服务。

## 第一阶段
爬取人脸图片的核心思路就是获取中国明星的名字，然后使用明星的名字作为图片搜索的关键字进行获取图片，然后删除下载过程损坏的图片和没有包含人脸的图片，或者过多人脸的图片（我们只保存一张图片只包含一张人脸的图片）。

首先获取中国明星的名字，该功能主要在`get_star_name.py`中实现。获取明显的名字核心代码如下，获取的名字不能保证百分之百正确，所以可能需要手动去检查。
```python
# 获取明星的名字并保存到文件中
def get_page(pages, star_name):
    params = []
    # 设置访问的请求头，包括分页数和明星所在的地区
    for i in range(0, 12 * pages + 12, 12):
        params.append({
            'resource_id': 28266,
            'from_mid': 1,
            'format': 'json',
            'ie': 'utf-8',
            'oe': 'utf-8',
            'query': '明星',
            'sort_key': '',
            'sort_type': 1,
            'stat0': '',
            'stat1': star_name,
            'stat2': '',
            'stat3': '',
            'pn': i,
            'rn': 12})

    # 请求的百度接口获取明星的名字
    url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php'

    x = 0
    # 根据请求头下载明星的名字
    for param in params:
        try:
            # 获取请求数据
            res = requests.get(url, params=param, timeout=50)
            # 把网页数据转换成json数据
            js = json.loads(res.text)
            # 获取json中的明星数据
            results = js.get('data')[0].get('result')
        except AttributeError as e:
            print('【错误】出现错误：%s' % e)
            continue

        # 从数据中提取明星的名字
        for result in results:
            img_name = result['ename']
            f.write(img_name + '\n',)
```


然后根据明星的名字从网上下载图片，该功能主要在`download_image.py`中实现，以下就是下载图片的核心代码片段。
```python
# 获取百度图片下载图片
def download_image(key_word, download_max):
    download_sum = 0
    str_gsm = '80'
    # 把每个明显的图片存放在单独一个文件夹中
    save_path = 'star_image' + '/' + key_word
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    while download_sum < download_max:
        # 下载次数超过指定值就停止下载
        if download_sum >= download_max:
            break
        str_pn = str(download_sum)
        # 定义百度图片的路径
        url = 'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&' \
              'word=' + key_word + '&pn=' + str_pn + '&gsm=' + str_gsm + '&ct=&ic=0&lm=-1&width=0&height=0'
        try:
            # 获取当前页面的源码
            result = requests.get(url, timeout=30).text
            # 获取当前页面的图片URL
            img_urls = re.findall('"objURL":"(.*?)",', result, re.S)
            if len(img_urls) < 1:
                break
            # 把这些图片URL一个个下载
            for img_url in img_urls:
                # 获取图片内容
                img = requests.get(img_url, timeout=30)
                img_name = save_path + '/' + str(uuid.uuid1()) + '.jpg'
                # 保存图片
                with open(img_name, 'wb') as f:
                    f.write(img.content)
                with open('image_url_list.txt', 'a+', encoding='utf-8') as f:
                    f.write(img_name + '\t' + img_url + '\n')
                download_sum += 1
                if download_sum >= download_max:
                    break
        except Exception as e:
            download_sum += 1
            continue
```


下载图片完成之后，有很多损坏的图片，需要把这些损坏的图片删除，该功能主要在`delete_error_image.py`实现。下面是删除损坏图片的核心代码片段。
```python
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
```

下载的图片中可能没有人脸，或者包含多张人脸，所以我们要把这些图片删除掉，该功能主要在`delete_more_than_one.py`中实现。删除没有人脸或者过多人脸图片的关键代码片段如下。
```python
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
```


## 第二阶段
第二阶段属于高级清理和标注人脸信息。这一个阶段首先是把每个文件夹中包含相同一个人的图片较多的人脸，选择其中一个作为主人脸图片。然后使用这个主图片来对比其他图片，判断是否是同一个人，如果不是就删除该图片。接着就删除URL文件中，一些删除的文件对应的URL。最好就使用百度的人脸检测服务标注清理后的图片，最终得到一个人脸数据集。

首先是从众多图片中选择一个主图片，这个功能主要在`find_same_person.py`中实现，以下是获取主图片的核心代码片段。这个程序消耗时间比较多，其实也可以通过手动标记的方式，选择一个主的人脸图片，当然这个是非常大的一个工作量。
```python
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
        except:
            os.remove(img_path)

    for image_path in image_paths:
        try:
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
        except:
            pass
```

然后删除与主图片不是同一个人的图片，这个功能主要在`delete_not_same_person.py`中实现，以下是删除不是同一个人脸的图片核心代码片段。
```python
    name_paths = os.listdir(father_path)
    # 确保全部文件夹都下的图片都标记了
    if check_if_all_rename(father_path, name_paths):
        for name_path in name_paths:
            print('正在对比 %s 图片...' % name_path)
            image_paths = os.listdir(os.path.join(father_path, name_path))
            # 正确图片的路径
            main_image = os.path.join(father_path, name_path, '0.jpg')
            main_img = face_recognition.load_image_file(main_image)
            main_encodings = face_recognition.face_encodings(main_img, num_jitters=100)[0]
            for image_path in image_paths:
                # 要对比的图片
                img_path = os.path.join(father_path, name_path, image_path)
                image = face_recognition.load_image_file(img_path)
                unknown_encoding = face_recognition.face_encodings(image, num_jitters=100)[0]
                results = face_recognition.compare_faces([main_encodings], unknown_encoding, tolerance=0.5)
                if not results[0]:
                    os.remove(img_path)
            shutil.move(src=os.path.join(father_path, name_path), dst=os.path.join('star_image', name_path))
        print('对比完成')
```

然后执行`delete_surplus_url.py`程序，从`image_url_list.txt`中删除本地不存在图片对应的URL。
```python
    # 删除图片过少的文件夹
    delete_too_few()
    list_path = 'image_url_list.txt'
    lines = get_txt_list(list_path)
    # 重新改写这个文件
    with open(list_path, 'w', encoding='utf-8') as f:
        for line in lines:
            exist = file_if_exist(line)
            # 把存在的文件的list保留
            if exist:
                f.write(line)
```

最后执行`annotate_image.py`程序，利用百度人脸检测接口标注人脸图片，以下是标注人脸的核心代码片段。
```python
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
        # 4个关键点位置，左眼中心、右眼中心、鼻尖、嘴中心
        landmark = str(result['result']['face_list'][0]['landmark']).replace("'", '"')
        # 拼接成符合json格式的字符串
        txt = '{"name":"%s", "image_url":"%s","age":%f, "gender":"%s", "glasses":"%s", "expression":"%s", "beauty":%f, "face_shape":"%s", "location":%s, "angle":%s, "landmark72":%s, "landmark":%s}' \
              % (name, image_url, age, gender, glasses, expression, beauty, face_shape, location, angle, landmark72,
                 landmark)
        # 转换成json数据并格式化
        json_dicts = json.loads(txt)
        json_format = json.dumps(json_dicts, sort_keys=True, indent=4, separators=(',', ':'))
        # 写入标注文件
        with open(annotation_file_path, 'w', encoding='utf-8') as f_a:
            f_a.write(json_format)
    except Exception as e:
        os.remove(image_path)
        pass
```

整个项目完成的时间的非常久的，特别是使用到百度AI服务的程序，为了不出现每秒访问次数超过2次（免费的版本是每秒自动访问2次），所在做了休眠处理，所以这样浪费了不少时间。


# 使用方法
在Ubuntu下分别执行：
```bash
python3 run_get_image_code.py
python3 run_annotate_image.py
```

# 免责声明
1. 使用该项目制作人脸数据集必须遵守中国法律法规。
2. 本项目使用的百度的人脸服务，也必须遵守百度的AI开放平台服务协议。
3. 本项目仅提供学习使用，禁止用于商业等其他盈利用于其他用途
4. 请各位使用者合法使用，否则造成的一切后果由使用者自行承担，本人不承担任何法律责任。
