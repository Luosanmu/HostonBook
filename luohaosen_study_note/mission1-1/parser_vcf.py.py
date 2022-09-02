# @Time : 2022/6/16 15:02
# @Author : ZhaoqiWu
# @File : parser_vcf.py
import optparse
import pandas as pd


def parser_vcf(vcf_path, output_path, skiprows=38):
    # 读取VCF文件
    if vcf_path.endswith(".gz"):
        df_raw = pd.read_table(vcf_path, compression='gzip', skiprows=skiprows)
    else:
        df_raw = pd.read_table(vcf_path, skiprows=38)
    # 获取part1
    df_part1 = df_raw[list(df_raw.columns)[:-2]]
    # 获取part2
    df_part2 = df_raw['Sample'].str.split(":", expand=True)
    # 合并
    df_new = pd.concat([df_part1, df_part2], axis=1)
    # 重命名列名
    df_new.columns = list(df_raw.columns)[:-2] + df_raw.loc[0, "FORMAT"].split(':')
    # 保存
    df_new.to_csv(output_path, sep='\t', index=False)


def main():
    list_vcf_path = ['./sample_5194_HBA.vcf',
                     './sample_5195_GJB2.vcf',
                     './sample_5196_MYO15A.vcf']
    for vcf_path in list_vcf_path:
        output_path = vcf_path.split('.')[0] + '.tsv'
        parser_vcf(vcf_path=vcf_path, output_path=output_path)


if __name__ == '__main__':
    parse = optparse.OptionParser(usage='"%prog"', version="%prog V1.0")
    parse.add_option("--v", "--vcf", dest="vcf_path", default='na', help="The path of vcf file")
    parse.add_option("--o", "--output", dest="output_path", default='na', help="The path of output file")
    options, args = parse.parse_args()
    if options.vcf_path == 'na':
        # 处理此次的三个VCF文件
        main()
        # 命令行示例：python parser_vcf.py
    else:
        # 处理后续任意输入的VCF文件
        parser_vcf(vcf_path=options.vcf_path, output_path=options.output_path)
        # 命令行示例：python parser_vcf.py --v ./sample_5194_HBA.vcf.gz --o ./sample_5194_HBA.tsv
