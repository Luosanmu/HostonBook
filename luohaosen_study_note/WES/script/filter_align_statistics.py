# Time:22/08/16
# Author:Haosen Luo
# @File: filter_align_statistics.py
import os
import configparser
import re
from optparse import OptionParser

BIN = os.path.dirname(__file__) + '/'
file_config = configparser.ConfigParser()
file_config.read(BIN + 'config.ini')


class FilterAlignStatistics(object):
    def __init__(self, align_mode: str, threading: int, sample_abs_path='', result_dir='', genome_version='hg38',
                 q_min=20):
        # Software config
        self.bwa = file_config['Software']['bwa']
        self.samtools = file_config['Software']['samtools']
        self.fastp = file_config['Software']['fastp']
        # The parameter of software
        if re.search(re.compile(r'pe|se', re.I), align_mode):
            self.mode = align_mode.upper()
        else:
            raise Exception("The paired mode could be pe or se")
        self.threads = threading
        self.gv = genome_version
        self.ref_genome = file_config['Reference'][genome_version]
        self.min_quality = q_min
        # Create the directory to save results
        self.sample = sample_abs_path
        self.result_dir = result_dir if os.path.exists(result_dir) else os.system(f"mkdir -p {result_dir}")
        self.result_dir = self.result_dir if self.result_dir.endswith('/') else self.result_dir + '/'
        # The base rule of sample
        if self.sample.endswith(('.fq', '.gz', '.fastq')):
            # sample's parent dir
            self.sample_dir = '/'.join(self.sample.split('/')[:-1]) + '/'
            # sample basename which likes "file-01_R1.fq.gz" or "file-01.fq.gz"
            self.sample_basename = os.path.basename(self.sample)
            # sample basename no suffix which likes "file-01_R1" or "file-01"
            self.basename_no_suffix = self.sample_basename.split(".")[0]
        else:
            raise Exception("The file format must be '.fq', '.gz', '.fastq'")
        # The special rule of sample
        if self.mode == 'SE':
            """
            单末端测序的fq文件举例
            假设一个样本文件是：xxx-01.fq.gz
            """
            self.sample_R_in = self.sample
            # create new sample result path for each sample
            self.each_result_path = self.result_dir + self.basename_no_suffix + '/'
            os.system(f"mkdir -p {self.each_result_path}")
            self.sample_C_out = self.each_result_path + self.basename_no_suffix + '.clean.fq.gz'
            self.bam_outfile = self.each_result_path + self.basename_no_suffix + '.bam'
            self.rmdup_bam_file = self.each_result_path + self.basename_no_suffix + '.rmdup.bam'
            self.json = self.each_result_path + self.basename_no_suffix + '.json'
            self.html = self.each_result_path + self.basename_no_suffix + '.html'
        elif self.mode == 'PE':
            """
            /modify/
            双末端测序的fq文件举例
            假设两个样本文件是：xxx-01_R1.fq.gz和xxx-01_R2.fq.gz, 这个地方需要根据实际双样本名称进行更改
            """
            self.sample_id, self.R12 = self.basename_no_suffix.split("_")
            self.each_result_path = self.result_dir + self.sample_id + '/'
            os.system(f"mkdir -p {self.each_result_path}")
            self.sample_R_1 = self.each_result_path + self.sample_id + '_R1.fq.gz'
            self.sample_R_2 = self.each_result_path + self.sample_id + '_R2.fq.gz'
            self.sample_C_1 = self.each_result_path + self.sample_id + '_R1.clean.fq.gz'
            self.sample_C_2 = self.each_result_path + self.sample_id + '_R2.clean.fq.gz'
            self.bam_outfile = self.each_result_path + self.sample_id + '.bam'
            self.rmdup_bam_file = self.each_result_path + self.sample_id + '.rmdup.bam'
            self.json = self.each_result_path + self.sample_id + '.json'
            self.html = self.each_result_path + self.sample_id + '.html'

        self.outpath_no_suffix = self.bam_outfile.split(".")[0]
        # samtools output flagstat setting
        self.flagstat_file = self.outpath_no_suffix + '.bam.flagstat'
        # self.rmdup_flagstat_file = self.outpath_no_suffix + '.rmdup.bam.flagstat'
        """ Program Beginning """
        # step1: Use fastp to filter low seq
        self.filter_func = self.fastp_filter()
        # step2: BWA align
        self.align_func = self.run_alignment()
        # step3: Statistics
        self.flagstat_func = self.get_bam_flagstat_file
        # self.rm_flagstat_func = self.get_rmdup_flagstat_file()
        """ reads_num and map ratio """
        self.total_read_num = self.get_reads_num(mapping=False)
        self.map_reads_num = self.get_reads_num(mapping=True)
        self.map_ratio = self.map_reads_num / self.total_read_num
        """ duplicate num and dup_ratio """
        self.rmdup_func = self.get_rmdup_bam_file
        self.dup_num = self.get_dup_reads_num
        self.dup_ratio = self.dup_num / self.map_reads_num
        """ MT reads num and ratio"""
        self.chr_m_num, self.chr_no_m_num, self.chr_m_ratio = self.get_mt_info
        """ Statistics: reads, total, total_gc , genome mean depth """
        # step4: Save the statistics result
        self.save_statistics_log()

    def fastp_filter(self):
        if self.mode == 'SE':
            # Single-End
            return os.system(
                f"{self.fastp} -i {self.sample_R_in} -o {self.sample_C_out} "
                f" -q {self.min_quality} -w {self.threads} -j {self.json} -h {self.html}")
        elif self.mode == 'PE':
            # Paired-End
            return os.system(
                f"{self.fastp} -i {self.sample_R_1} -o {self.sample_C_1} -I {self.sample_R_2} -O {self.sample_C_2} "
                f"-q {self.min_quality} -w {self.threads} -j {self.json} -h {self.html} ")

    def run_alignment(self):
        # 将过滤了低质量的序列进行BWA比对
        if self.mode == 'SE':
            return os.system(
                "{bwa} mem -t {threading} -M -P -R '@RG\\tID:{basename_no_suffix}\\tPL:Illumina\\tSM:wes' "
                "{refseq} {sample_seq} | "
                "{samtools} sort -o {bam_output_path} ".format(bwa=self.bwa,
                                                               threading=self.threads,
                                                               basename_no_suffix=self.basename_no_suffix,
                                                               refseq=self.ref_genome,
                                                               sample_seq=self.sample_C_out,
                                                               samtools=self.samtools,
                                                               bam_output_path=self.bam_outfile))
        elif self.mode == 'PE':
            return os.system(
                "{bwa} mem -t {threading} -M -P -R '@RG\\tID:{sample_id}\\tPL:Illumina\\tSM:wes' "
                "{refseq} {sample_c_1} {sample_c_2} "
                "| {samtools} sort -o {bam_output_path} ".format(bwa=self.bwa,
                                                                 threading=self.threads,
                                                                 sample_id=self.sample_id,
                                                                 refseq=self.ref_genome,
                                                                 sample_c_1=self.sample_C_1,
                                                                 sample_c_2=self.sample_C_2,
                                                                 samtools=self.samtools,
                                                                 bam_output_path=self.bam_outfile))

    @property
    def get_bam_flagstat_file(self):
        # 用来做后续的统计验证
        return os.system("{samtools} flagstat {bam_file} > {flagstat_out}".format(samtools=self.samtools,
                                                                                  bam_file=self.bam_outfile,
                                                                                  flagstat_out=self.flagstat_file))

    # @property
    # def get_rmdup_flagstat_file(self):
    #     # 同get_bam_flagstat_file
    #     return os.system("{samtools} flagstat {rm_file} > {rm_flagstat}".format(samtools=self.samtools,
    #                                                                             rm_file=self.rmdup_bam_file,
    #                                                                             rm_flagstat=self.rmdup_flagstat_file))

    # Beginning this step, which is the statistics for NGS information
    def get_reads_num(self, mapping=False):
        if mapping:
            if self.mode == 'SE':
                return int(os.popen(f"{self.samtools} view -F 4  {self.bam_outfile} | wc -l").read().strip())
            elif self.mode == 'PE':
                return int(os.popen(f"{self.samtools} view -F 12 {self.bam_outfile} | wc -l").read().strip())
        else:
            if self.mode == 'SE':
                return int(os.popen(f"less -S {self.sample_C_out} | wc -l").read().strip()) / 4
            elif self.mode == 'PE':
                return int(os.popen(f"less -S {self.sample_C_1} | wc -l").read().strip()) / 4

    @property
    def get_rmdup_bam_file(self):
        argv = '-S' if self.mode == 'PE' else '-s'
        return os.system(f"{self.samtools} rmdup {argv} {self.bam_outfile} {self.rmdup_bam_file}")

    @property
    def get_rmdup_reads_num(self):
        rmdup_bam_file = self.outpath_no_suffix + '.rmdup.bam'
        return int(os.popen(f"{self.samtools} view -F 4 {rmdup_bam_file} | wc -l").read().strip())

    @property
    def get_dup_reads_num(self):
        map_reads_num = int(os.popen(f"{self.samtools} view -F 4 {self.bam_outfile} | wc -l").read().strip())
        rmdup_reads_num = self.get_rmdup_reads_num
        return map_reads_num - rmdup_reads_num

    @property
    def get_mt_info(self):
        chr_m_num = 0
        chr_no_m_num = 0
        bam_data = os.popen("{samtools} view {bam_file} | less".format(samtools=self.samtools,
                                                                       bam_file=self.bam_outfile)).readlines()
        for line in bam_data:
            plain_text = line.strip().split('\t')
            if plain_text[2] == '*':
                continue
            elif plain_text[2] == 'chrM':
                chr_m_num += 1
            else:
                chr_no_m_num += 1
        return chr_m_num, chr_no_m_num, chr_m_num / (chr_m_num + chr_no_m_num)

    @property
    def statistics_bam(self):
        genome, total, total_a, total_g, total_c, total_t, total_gc, reads = 0, 0, 0, 0, 0, 0, 0, 0
        bam_data = os.popen(f"{self.samtools} view -h {self.bam_outfile} | less").readlines()
        for line in bam_data:
            if line.startswith("@"):
                if line.startswith("@SQ"):
                    if 'chrM' not in line:
                        # 取 LN:(\d+)
                        genome += int(line.strip().split("\t")[2].split(":")[1])
            else:
                bam_data = line.strip().split("\t")
                total += int(len(bam_data[9]))
                total_a += int(bam_data[9].count('A'))
                total_g += int(bam_data[9].count('G'))
                total_c += int(bam_data[9].count('C'))
                total_t += int(bam_data[9].count('T'))
                reads += 1
        total_gc = total_g + total_c

        return genome, total, total_a, total_g, total_c, total_t, total_gc, reads

    def save_statistics_log(self):
        genome, total, total_a, total_g, total_c, total_t, total_gc, reads = self.statistics_bam
        result_list = ['The statistics result is following:',
                       "Map ratio is {0:.2f}% = {1} / {2}".format(self.map_ratio * 100,
                                                                  self.map_reads_num, self.total_read_num),
                       "Duplicate ratio is {0:.2f}% = {1} / {2}".format(self.dup_ratio * 100,
                                                                        self.dup_num, self.map_reads_num),
                       "MT ratio is {0:.3f}% = {1} / {2}".format(self.chr_m_ratio * 100,
                                                                 self.chr_m_num, self.chr_no_m_num + self.chr_m_num),
                       "#" * 100,
                       "Total reads num is {0}".format(reads),
                       "Genome mean depth is {0:.3f} = {1} / {2}".format(total / genome, total, genome),
                       "Reads mean length is {0:.2f} = {1} / {2}".format(total / reads, total, reads),
                       "GC rate is {0:.2f}% = {1} / {2}".format(total_gc * 100 / total, total_gc, total),
                       ]

        with open(self.outpath_no_suffix + ".log", "w") as f_log:
            for line in result_list:
                f_log.write(line + "\n")


# 仅用于测试代码
def main():
    list_sample = ['YF22051201-07.fq.gz']

    data_source = '/ifs1/data/WES/YF_hearingloss/'
    result_dir = '/ifs1/home/luohaosen/project/WES/result'
    for sample in list_sample:
        sample_each_path = data_source + sample
        FilterAlignStatistics(align_mode='SE', threading=4, sample_abs_path=sample_each_path, result_dir=result_dir,
                              genome_version='hg38', q_min=30)


if __name__ == '__main__':
    parser = OptionParser(usage='%prog [-h]', version='%prog v1.0', description='Filter,Align and Statistics')
    parser.add_option("--m", "--mode", dest="align_mode", default='se', help="The mode of align having pe or se")
    parser.add_option("--t", "--threads", dest="threading", default=1,  help="The running threading num")
    parser.add_option("--i", "--input", dest="sample_abs_path", default='na', help="The abspath of raw samples")
    parser.add_option("--o", "--output", dest="result_dir", default='na', help="The directory of result")
    parser.add_option("--g", "--genome_version", dest="genome_version", default='hg38', help="The reference fa file")
    parser.add_option("--q", "--Min_Quality", dest="q_min", default=20, type=int, help="The Min of base quality value")
    options, args = parser.parse_args()
    if options.sample_abs_path == 'na':
        main()
    else:
        # filter fastq and run seq alignment
        FilterAlignStatistics(align_mode=options.align_mode,
                              threading=options.threading,
                              sample_abs_path=options.sample_abs_path,
                              result_dir=options.result_dir,
                              genome_version=options.genome_version,
                              q_min=options.q_min)
