import os
import shutil


# 获取文件中的列表
def get_txt_list(list_path):
    with open(list_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines


# 判断文件是否存在
def file_if_exist(line):
    image_path, _ = line.split('\t')
    return os.path.exists(image_path)


# 删除图片过少的文件夹
def delete_too_few():
    father_path = 'star_image'
    name_paths = os.listdir(father_path)
    for name_path in name_paths:
        image_paths = os.listdir(os.path.join(father_path, name_path))
        if len(image_paths) < 5:
            shutil.rmtree(os.path.join(father_path, name_path), ignore_errors=False)


if __name__ == '__main__':
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
