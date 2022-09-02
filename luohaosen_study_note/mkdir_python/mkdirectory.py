# Time: 2022/07/08
# Author: Hoston Luo
# Filename: mkdirectory.py
# Function: create some directory like 'fold_{number}', number is from 1 to the end you want
import os
import re
import shutil
from optparse import OptionParser


def make_dir(plan_path, main_dir_num, secondary_dir_num,
             main_dir_font_frame, second_dir_font_frame):
    # step1: 希望创建存在"特定字符"的第一级目录
    want_main_dir = [f"{main_dir_font_frame}_{k + 1}" for k in range(main_dir_num)]
    i = 1
    # step2: 按照step1创建的包含特定样式的列表，按照名单，在plan_path下逐一创建相应的目录
    for filename in want_main_dir:
        if filename not in os.listdir(plan_path):
            os.mkdir(f"./{main_dir_font_frame}_{i}")
            for j in range(secondary_dir_num):
                os.mkdir(f"./{main_dir_font_frame}_{i}/{second_dir_font_frame}_{j + 1}")
                continue
        i += 1


def remove_dir(plan_path, remove_main_dir_prefix):
    """
    step3: 如果只是创建一次，其实上面的函数已经够用了，但是如果我因为创建错误，需要更改创建的数量，我的方法就是删除原来的并重新创建
    """
    # 防止误删其他文件，而只需要删除曾经创建的文件，这边结合了正则表达式，筛选出符合要求的文件夹名称
    need_to_remove_dir = [r for r in os.listdir(plan_path) if os.path.isdir(r) and '.idea' != r]
    for f in need_to_remove_dir:
        if re.search(pattern=rf'{remove_main_dir_prefix}_.*', string=f, flags=re.I):
            # 递归删除文件夹，这个在前面做了正则筛选，保证不会误删当前路径下的其他文件夹，仅删除需要的上一个文件夹
            shutil.rmtree(f)


def main():
    # 删除上一次创建的文件，可以自己根据实际情况设置
    remove_dir('.', remove_main_dir_prefix='font')
    make_dir('.', main_dir_num=5, secondary_dir_num=5, main_dir_font_frame='folder', second_dir_font_frame='folder')


if __name__ == '__main__':
    parse = OptionParser()
    parse.add_option('-p', dest='plan_path', default='na', help="The path you want to create")
    parse.add_option('-m', dest='main_dir_num', default=5, type=int, help="The main dir number you want, type=int")
    parse.add_option('-s', dest='secondary_dir_num', default=5, type=int, help="The secondary dir number,type=int")
    parse.add_option('-r', dest='remove_main_dir_prefix', default='na', help="The prefix You need to remove")
    parse.add_option('-b', dest='main_font_frame', default='na', help="The main dir name's prefix")
    parse.add_option('-a', dest='second_font_frame', default='na', help="The second dir name's prefix")

    option, arg = parse.parse_args()
    if option.plan_path == 'na':
        main()
    else:
        # 命令行示例：python mkdirectory.py -p './' -m  -s 5 -r 'font' -b 'folder' -a 'folder'
        remove_dir(plan_path=option.plan_path, remove_main_dir_prefix=option.remove_main_dir_prefix)
        make_dir(plan_path=option.plan_path, main_dir_num=option.main_dir_num,
                 secondary_dir_num=option.secondary_dir_num,
                 main_dir_font_frame=option.main_font_frame,
                 second_dir_font_frame=option.second_font_frame)
