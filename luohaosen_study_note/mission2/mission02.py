# Time: 2022/06/28 ~ 2022/06/30
# Author: Haosen Luo
# Filename: mission02.py
import pandas as pd
import os
from optparse import OptionParser


def read_txt(filepath, special_field=''):
    # step1: 遍历输入文件位置，读取符合特定文件名的文件
    for input_file in os.listdir(filepath):
        if special_field in input_file:
            data_raw = pd.read_table(input_file, sep="\t", skiprows=9, dtype=str)
            # step2: 筛选需求相关列
            df_snp_name = data_raw["SNP Name"]
            df_chr = data_raw["Chr"]
            df_position = data_raw["Position"]
            df_sample_id = data_raw["Sample ID"]
            df_allele_plus = data_raw["Allele1 - Plus"] + data_raw["Allele2 - Plus"]
            # 合并数据
            df_demo = pd.concat([df_snp_name, df_chr, df_position, df_sample_id, df_allele_plus], axis=1)
            # 修改列名
            df_demo.columns = ["gxid", "chromosome", "position", "sample_id", "allele"]
            # step3: 找出文件中的sample_id列有5个唯一的样本编号
            sample_uniq_id = list(df_sample_id.unique())

            return df_demo, sample_uniq_id


def main(output_file_path='./final_test.txt'):
    # 调用read_txt函数的结果作为本函数的变量
    df_demo, sample_uniq_id = read_txt(filepath='./', special_field='FinalReport_standard')
    # 根据行号均分成5份，分别做sample_id的表，下述方法的缺点在于依赖样本均匀，目前在想如何不依赖样本的分布制表
    frame_spilt_rows = int(len(df_demo) / len(sample_uniq_id))
    # 对应名称索引值+1就是位置
    df_lsy_sample = df_demo[: (sample_uniq_id.index('LSY') + 1) * frame_spilt_rows]
    df_lyj_sample = df_demo[(sample_uniq_id.index('LSY') + 1) * frame_spilt_rows: (sample_uniq_id.index(
        'LYJ') + 1) * frame_spilt_rows]
    df_lwx_sample = df_demo[(sample_uniq_id.index('LYJ') + 1) * frame_spilt_rows: (sample_uniq_id.index(
        'LWX') + 1) * frame_spilt_rows]
    df_lxy_sample = df_demo[(sample_uniq_id.index('LWX') + 1) * frame_spilt_rows: (sample_uniq_id.index(
        'LXY') + 1) * frame_spilt_rows]
    df_poc23_yf_sample = df_demo[(sample_uniq_id.index('LXY') + 1) * frame_spilt_rows:]

    # step3: 遍历后分别将分型结果储存为一个list,共5个list
    df_lsy = [df_lsy_sample["allele"].tolist() for i in sample_uniq_id if i == 'LSY']
    df_lyj = [df_lyj_sample["allele"].tolist() for i in sample_uniq_id if i == 'LYJ']
    df_lwx = [df_lwx_sample["allele"].tolist() for i in sample_uniq_id if i == 'LWX']
    df_lxy = [df_lxy_sample["allele"].tolist() for i in sample_uniq_id if i == 'LXY']
    df_poc23_yf = [df_poc23_yf_sample["allele"].tolist() for i in sample_uniq_id if i == 'POC23_YF']

    # step4: 生成最终的结果表格并导出为txt格式
    final_df = pd.DataFrame(dict(
        gxid=df_demo["gxid"].drop_duplicates(),
        chromosome=df_demo["chromosome"][: frame_spilt_rows],
        position=df_demo["position"][: frame_spilt_rows],
        LSY=df_lsy[0],
        LYJ=df_lyj[0],
        LWX=df_lwx[0],
        LXY=df_lxy[0],
        POC23_YF=df_poc23_yf[0]),
    )
    print(final_df)
    final_df.to_csv(output_file_path, sep='\t', index=False)


if __name__ == '__main__':
    # 尝试写了一下在linux环境下运行的脚本,可能运行不了
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="filepath", default="na", help="The file input path", )
    parser.add_option("-o", "--output", dest="output_file_path", default="na", help="The file output path")
    parser.add_option("-s", "--special", dest="special_field", default="na", help="The special field of filename")
    options, args = parser.parse_args()
    if options.filepath == "na":
        main()
    else:
        # 命令行示例：python mission02.py -i ./  --output final_test.txt  -s 'FinalReport_standard'
        read_txt(filepath=options.filepath, special_field=options.special_field)
        main(output_file_path=options.output_file_path)