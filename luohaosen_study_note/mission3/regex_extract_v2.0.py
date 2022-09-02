# Time:2022/07/04
# Author:Haosen Luo
# Filename:coding_extract.py
import pandas as pd
import re
from optparse import OptionParser


def regex_extract(input_filename_path, file_output_path):
    """
    :param input_filename_path: 文件输入路径
    :param file_output_path: 文件输出路径
    """
    # Step1: 读取需要分析的核型书写文件
    data_row = pd.read_table(input_filename_path, sep='\t', header=None, dtype=str)
    data_row = data_row[0].tolist()
    # Step2: 通过条件解析式得到df数据的列表，不够优雅但是技穷了
    df_plmi = []
    df_chrom = []
    df_mos = []
    df_start = []
    df_end = []
    df_length = []
    df_fold = []

    for i in range(len(data_row)):
        line = data_row[i]
        # Step3: 根据正则表达式匹配
        plim_regex = re.search(pattern='[+-](?=\w)', string=line, flags=0)
        chrom_regex = re.search(pattern='(?<=[+-])\w+(?=\{)', string=line, flags=0)
        start_regex = re.search(pattern='(?<=\{)[qp]\d+\.?\d+(?=-)', string=line, flags=0)
        end_regex = re.search(pattern='(?<=\>)[qp]\d+\.?\d+(?=\()', string=line, flags=0)
        length_regex = re.search(pattern='(?<=\()\d+\.+\d+(?=Mb)', string=line, flags=0)
        fold_regex = re.search(pattern='(?<=×)\d+', string=line, flags=0)
        mos_regex = re.search(pattern='(?<=\[)\d.*%', string=line, flags=re.IGNORECASE)

        df_plmi.append(plim_regex.group()) if plim_regex else df_plmi.append('')
        df_chrom.append(chrom_regex.group()) if chrom_regex else df_chrom.append('')
        df_start.append(start_regex.group()) if start_regex else df_start.append('')
        df_end.append(end_regex.group()) if end_regex else df_end.append('')
        df_length.append(length_regex.group()) if length_regex else df_length.append('')
        df_fold.append(fold_regex.group()) if fold_regex else df_fold.append('')
        df_mos.append(mos_regex.group()) if mos_regex else df_mos.append('')

    # Step4: 合并dataframe并导出
    df = pd.DataFrame(dict(
        result=data_row,
        plmi=df_plmi,
        chrom=df_chrom,
        start=df_start,
        end=df_end,
        length=df_length,
        fold=df_fold,
        mos=df_mos))
    print(df.head())
    df.to_csv(file_output_path, sep='\t', index=False)


def main():
    regex_extract(input_filename_path='./coding3_raw.txt',
                  file_output_path='./result.txt')


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-i', '--input', dest='file_input_path', default='na', help="The path of file to be processed")
    parser.add_option('-o', '--output', dest='file_output_path', default='na', help="The path of file to be save")
    options, args = parser.parse_args()
    if options.file_input_path == 'na':
        main()
    else:
        # linux命令行示例：python coding_extract.py -i './coding3_raw.txt' -o './result.txt'
        regex_extract(input_filename_path=options.file_input_path,
                      file_output_path=options.file_output_path)
