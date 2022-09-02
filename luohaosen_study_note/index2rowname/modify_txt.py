# Time: 2022/07/25 21:49
# Author: HaosenLuo
# @File: parser_CN.py
import pandas as pd
from optparse import OptionParser
from addict import Dict
pd.set_option('display.max_columns', 10)
pd.set_option('expand_frame_repr', False)


def modify_txt(input_path, output_path):
    txt = pd.read_table(input_path)
    # step1: 获取列名
    txt_part_col = txt.columns.values[1:]
    # step2: 获取行名
    txt_part_row = txt['GeneName'].tolist()
    # step3: 一列列的获取数据，构建字典的键值对
    data_dict = Dict()
    for col_name in txt_part_col:
        data_dict[col_name] = txt[col_name].tolist()
    # step4: 构建dataframe
    df = pd.DataFrame(data=data_dict, index=txt_part_row)
    # step5: 保存文件，自个在后面更改格式
    df.to_csv(output_path, sep='\t')


def main():
    modify_txt(input_path='./1.txt', output_path='./result_gn.txt')


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--i", "--input", dest="input_path", default='NA', help="The File you need process")
    parser.add_option("--o", "--output", dest="output_path", default='NA', help="The site you output")
    options, arg = parser.parse_args()
    if options.input_path == 'NA':
        main()
    else:
        # 命令行示例: python parser_GN.py --i "./1.txt" --o "./result_gn.txt"
        modify_txt(input_path=options.input_path, output_path=options.output_path)
