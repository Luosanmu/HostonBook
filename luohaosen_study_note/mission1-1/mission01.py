# 在linux上，使用了cp命令，将vcf文件转化成了目标txt文件
## step 1 : 编写一个shell脚本改后缀
## vi biancheng01.sh
## files=$(ls ./*.vcf)
## for file in $files
## do
##      cp $file ${file%.vcf}.txt
## done
## chmod 755 biancheng01.sh
## ./biancheng01.sh

# step 2 : 编写一个python脚本，用于构建数据框
import numpy as np
import io
import os
import pandas as pd


def build_df(filename):
    # 读取txt文件
    file = pd.read_csv(filename, sep='\t')
    data = file
    df = pd.DataFrame(data=data,
                      columns=["#CHROM", "POS", "ID", "REF",
                               "ALT", "QUAL", "FILTER", "INFO"])

    # 列出要处理的数据，各做一个list
    GT = []
    GQ = []
    DP = []
    AD = []
    VAF= []
    C = []

    # 循环读取“：”分隔的数据
    for i in range(len(file)):
        GT.append(file.Sample.str.split(":", 6)[i][0])
        GQ.append(file.Sample.str.split(":", 6)[i][1])
        DP.append(file.Sample.str.split(":", 6)[i][2])
        AD.append(file.Sample.str.split(":", 6)[i][3])
        VAF.append(file.Sample.str.split(":", 6)[i][4])
        C.append(file.Sample.str.split(":", 6)[i][5])

    # 在原有的dataframe的右边添加GT\GQ\DP\AD\VAF\C列
    df = df.assign(GT=GT)
    df = df.assign(GQ=GQ)
    df = df.assign(DP=DP)
    df = df.assign(AD=AD)
    df = df.assign(VAF=VAF)
    df = df.assign(C=C)

    return df


# step 3 : 分别导出数据框
df1 = build_df('sample_5194_HBA.txt')
df2 = build_df('sample_5195_GJB2.txt')
df3 = build_df('sample_5196_MYO15A.txt')

# step 4 : 将dataframe格式导出为csv文件,并且是以\t作为分隔的tsv文件
df1.to_csv(path_or_buf='./sample_5194_HBA.tsv',
           sep='\t',
           header=["#CHROM", "POS", "ID", "REF",
                   "ALT", "QUAL", "FILTER", "INFO",
                   "GD", "GQ", "DP", "AD", "VAF", "C"],
           index=False)

df2.to_csv(path_or_buf='./sample_5195_GJB2.tsv',
           sep='\t',
           header=["#CHROM", "POS", "ID", "REF",
                   "ALT", "QUAL", "FILTER", "INFO",
                   "GD", "GQ", "DP", "AD", "VAF", "C"],
           index=False)

df2.to_csv(path_or_buf='./sample_5196_MYO15A.tsv',
           sep='\t',
           header=["#CHROM", "POS", "ID", "REF",
                   "ALT", "QUAL", "FILTER", "INFO",
                   "GD", "GQ", "DP", "AD", "VAF", "C"],
           index=False)