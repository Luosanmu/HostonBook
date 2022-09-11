# Time: 22/09/05 22:51
# Author: Haosen Luo
# @File: chrom_statistics.py
import pandas as pd
import re
from optparse import OptionParser


class ChrStatistics(object):
    def __init__(self, excel_file, output_file):
        self.input_file = excel_file
        self.output_file = output_file
        self.save_result()

    @property
    def read_excel(self):
        data = pd.read_excel(self.input_file)
        return data['result_raw']

    @property
    def chr_statistics(self):
        chr_n = ['chr' + str(i) for i in range(1, 23)] + ['chrX', 'chrY', 'total']
        origin_data = self.read_excel
        # 染色体:数目
        dict_chr_num = dict(zip(chr_n, [0]*25))
        for line in origin_data:
            list_cyto = re.split(';', line)
            for i in range(len(list_cyto)):
                pattern_re = re.search(r'[+-](\d+){', string=list_cyto[i], flags=0)
                # 这一步很关键，我因为这一步没考虑，差点完成不了脚本
                digit = pattern_re.group(1) if pattern_re else 0
                if pattern_re:
                    chr_format_index = 'chr' + str(digit)
                    dict_chr_num[chr_format_index] += 1
                    dict_chr_num['total'] += 1
                else:
                    pass
        return dict_chr_num

    def save_result(self):
        dict_chr_num = self.chr_statistics
        # dataframe创建的方式不够熟悉，需要加强！
        new_table = pd.DataFrame(pd.Series(dict_chr_num), columns=['value'])
        new_table.to_csv(self.output_file, sep='\t')


def main():
    excel_file = 'D:\\Note\\origin_resource\\origin.xlsx'
    output_file = 'D:\\Note\\origin_resource\\origin.txt'
    ChrStatistics(excel_file=excel_file, output_file=output_file)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--i", "--input", dest='excel_file', default='na', help="The excel you want to process")
    parser.add_option("--o", "--output", dest='output_file', default='na', help="The output path of file")
    options, args = parser.parse_args()
    if options.excel_file == 'na':
        main()
    else:
        # 命令行实例： python ~/chrom_statistics.py --i /excel/path/xxx.xlsx --o /file/path/xxx.txt
        ChrStatistics(excel_file=options.excel_file, output_file=options.output_file)
