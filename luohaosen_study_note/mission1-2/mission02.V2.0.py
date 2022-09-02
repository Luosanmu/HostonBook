# Time:2022.06.22
# Author:LuoHaosen
# file:mission2.V2.O.py
import os
import time


def tf_file(source_file_path, save_file_path, need_str=' '):
    """
    :param source_file_path: 源文件路径
    :param save_file_path: 同步到的文件路径
    :param need_str: 文件名的筛选条件
    """
    # step1：筛选出‘object’字段的文件，并建构成一个含object字段文件的列表
    object_file_list_in_source = [filename for filename in os.listdir(source_file_path)
                                  if filename not in os.listdir(save_file_path) and need_str in filename]
    # step2：定期检查目录b是否含有object文件，有就不同步，没就同个步
    while True:
        for file in object_file_list_in_source:
            file1_path = os.path.join(source_file_path, file)
            file2_path = os.path.join(save_file_path)

            os.system(f"cp -r {file1_path} {file2_path}")

        time.sleep(30)


def main():
    tf_file(source_file_path='./dirA', save_file_path='./dirB', need_str="object")


if __name__ == '__main__':
    main()
