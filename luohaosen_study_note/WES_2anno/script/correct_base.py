# Time: 22/8/26 14:00
# Author: Haosen Luo
# @File: call_snp.py
import os
import configparser
from optparse import OptionParser

BIN = os.path.dirname(__file__) + '/'
file_config = configparser.ConfigParser()
file_config.read(BIN + 'config.ini')


class CorrectBase(object):
    def __init__(self, bam_input, result_dir, genome_version='hg38'):
        if bam_input.split('.')[1] == 'bam':
            # 排除.rmdup.bam的干扰
            self.bam_file = bam_input
        else:
            raise Exception("The input file is not '/path/sample_name.bam'")
        self.out_no_suffix = self.bam_file.split('.')[0]
        self.result_dir = result_dir
        self.WES_site = '/'.join(self.result_dir.split('/')[:-2]) + '/'
        # 用于存放java缓存tmp_dir
        tmp_dir = '/'.join(result_dir.split('/')[:-2]) + '/java_tmp/'
        self.tmp_dir = tmp_dir if os.path.exists(tmp_dir) else os.system(f"mkdir -p {tmp_dir}")
        self.genome = genome_version
        # ev means 'exon_version' 是安捷伦外显子参考版本
        self.ev = '_'.join((self.genome, 'v8'))
        self.exon_bed = file_config['Exon_bam'][self.ev]
        self.exon_interval = self.bam_file.split(".")[0] + '.Exon.Interval.bed'
        self.ref_genome = file_config['Reference'][self.genome]
        self.ref_dict = file_config['Build_dict'][self.genome]
        # Anno database parser
        self.gold = file_config['Annotation']['_'.join((self.genome, 'gold'))]
        self.dbsnp = file_config['Annotation']['_'.join((self.genome, 'dbsnp'))]
        # Software parameter
        self.gatk4 = file_config['Software']['gatk4']
        self.samtools = file_config['Software']['samtools']
        # Running
        self.exon_coverage_ratio()
        self.mark_pcr_dupseq()
        self.base_quality_score_recalibration()

    def exon_coverage_ratio(self):
        # step1: 构建参考基因组dict,因为pipeline的PGS_1M有,这边就不构建了
        # os.system(f"{self.gatk4} CreateSequenceDictionary -R {self.ref_genome} -O {self.ref_dict}")
        # step2: 将外显子bed文件(在安捷伦官网下载的)转化为外显子Interval文件
        os.system(f"{self.gatk4} BedToIntervalList -I {self.exon_bed} -O {self.exon_interval} -SD {self.ref_dict}")
        # step3: 计算外显子覆盖度等
        os.system(f"{self.gatk4} CollectHsMetrics -BI {self.exon_interval} -TI {self.exon_interval}  \
                   -I {self.bam_file} -O {self.out_no_suffix + '.stat.txt'}")

    def mark_pcr_dupseq(self):
        # 标记pcr重复
        os.system(f"{self.gatk4} --java-options '-Xmx10G -Djava.io.tmpdir={self.tmp_dir}' MarkDuplicates  \
                    -I {self.bam_file}  -O {self.out_no_suffix + '.MarkDuplicates.bam'}  \
                    -M {self.out_no_suffix + '.bam.metrics'} ")
        # 建立标记文件索引
        os.system(f"{self.samtools} index {self.out_no_suffix + '.MarkDuplicates.bam'}")

    # 碱基质量值校正
    def base_quality_score_recalibration(self):
        os.system(f"{self.gatk4} --java-options '-Xmx10G -Djava.io.tmpdir={self.tmp_dir}' BaseRecalibrator  \
                    -R {self.ref_genome} -I {self.out_no_suffix + '.MarkDuplicates.bam'}  \
                    --known-sites {self.gold}   --known-sites {self.dbsnp}     \
                    -L {self.exon_bed} -O {self.out_no_suffix + '.recal_data.table'}")
        os.system(f"{self.gatk4} --java-options '-Xmx10G -Djava.io.tmpdir={self.tmp_dir}' ApplyBQSR  \
                    -R {self.ref_genome} -I {self.out_no_suffix + '.MarkDuplicates.bam'}  \
                    -bqsr {self.out_no_suffix + '.recal_data.table'} -L {self.exon_bed}  \
                    -O {self.out_no_suffix + '.MarkDuplicates.BQSR.bam'}")
        # 下面的这条命令需要环境能运行 Rscript
        # os.system(f"{self.gatk4} AnalyzeCovariates -bqsr {self.out_no_suffix + '.recal_data.table'} "
        #           f" -plots {self.out_no_suffix + '.recal_data.table.plot'}")


# 仅用于测试代码
def main():
    result_dir = '/ifs1/home/luohaosen/project/WES/result/'
    for each_sample_dir in os.listdir(result_dir):
        each_sample_dir = result_dir + each_sample_dir
        for file in os.listdir(each_sample_dir):
            if file.split('.')[1] == 'bam':
                # 排除.rmdup.bam的干扰
                each_bam_file_path = result_dir + each_sample_dir + file
                CorrectBase(bam_input=each_bam_file_path, result_dir=result_dir, genome_version='hg38')
            else:
                break


if __name__ == '__main__':
    parser = OptionParser(usage='%prog [-h]', version='%prog v1.0', description='Mark dup seq and Recalibrate base')
    parser.add_option("--b", "--bam_input", dest='bam_input', default='na', type=str, help="The Bam file of align")
    parser.add_option("--o", "--output", dest="result_dir", type=str, help="The result path")
    parser.add_option("--g", "--genome_version", dest="genome_version", default='hg38', help="The ref genome version")
    options, args = parser.parse_args()
    if options.bam_input == 'na':
        main()
        # Snp and indel filter and annotation
    else:
        CorrectBase(bam_input=options.bam_input,
                    result_dir=options.result_dir,
                    genome_version=options.genome_version)
