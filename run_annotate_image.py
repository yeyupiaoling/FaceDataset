import os

# 寻找同一个人脸为主图片
os.system('python3 find_same_person.py')
# 删除同一个目录下不是相同人脸的图片
os.system('python3 delete_not_same_person.py')
# 删除已经清理的图片
os.system('python3 delete_surplus_url.py')
# 开始标注人脸图片
os.system('python3 annotate_image.py')