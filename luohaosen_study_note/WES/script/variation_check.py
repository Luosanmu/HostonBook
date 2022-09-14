# Time: 22/9/7 23:05
# Author: Haosen Luo
# Filename: variation_check.py
import os
import configparser
from optparse import OptionParser

BIN = os.path.dirname(__file__) + '/'
file_config = configparser.ConfigParser()
file_config.read(BIN + 'config.ini')


class VariantCheck(object):
    def __init__(self, bam_input, result_dir, genome_version='hg38', method=1, combine=''):
        if bam_input.split('.')[2] == 'BQSR' and bam_input.split('.')[3] == 'bam':
            # bam_file_path = /path/sample_basename.MarkDuplicates.BQSR.bam
            self.bam_file = bam_input
        else:
            raise Exception("The input path is not '/path/sample_name.MarkDuplicates.BQSR.bam'")
        self.out_no_suffix = self.bam_file.split('.')[0]
        self.result_dir = result_dir
        # 用于存放java缓存tmp_dir, such as  /ifs1/home/luohaosen/project/WES/java_tmp/
        self.WES_site = '/'.join(self.result_dir.split('/')[:-2]) + '/'
        self.tmp_dir = self.WES_site + 'java_tmp/'
        self.genome = genome_version
        self.method = method
        self.combine = combine
        # ev means 'exon_version' 是安捷伦外显子参考版本
        self.ev = '_'.join((self.genome, 'v8'))
        self.exon_bed = file_config['Exon_bam'][self.ev]
        self.ref_genome = file_config['Reference'][self.genome]
        # database
        self.dbsnp = file_config['Annotation']['_'.join((self.genome, 'dbsnp'))]
        # Software
        self.gatk4 = file_config['Software']['gatk4']
        self.annovar_covert = file_config['Annovar']['convert']
        self.annovar_table = file_config['Annovar']['table']
        # Running
        if method == 1:
            self.get_single_sample_raw_vcf()
            self.combine = 'n'
        elif method == 2:
            self.get_gvcf_for_combine()
            if self.combine == 'y':
                self.combine_all_gvcf_file()
                self.run_combine_command()
                self.get_raw_vcf_combine()
            elif self.combine == 'n':
                self.get_raw_vcf_no_combine()
            else:
                raise Exception("You should opt combine gvcf mode, y (yes) or n (no)")
        else:
            raise Exception("HaplotypeCaller has '1' and '2' method to check variation")

    """
    第一种方法: 只适合检测单样本以及样本量固定的情况
    """

    def get_single_sample_raw_vcf(self):
        return os.system(f"{self.gatk4} --java-options '-Xmx8G -Djava.io.tmpdir={self.tmp_dir}' HaplotypeCaller  \
                            -R {self.ref_genome}  -I {self.out_no_suffix + '.MarkDuplicates.BQSR.bam'}  \
                            -D {self.dbsnp}  -L {self.exon_bed}  -O {self.out_no_suffix + '.raw.vcf'}")

    """ 
    第二种方法: 生成中间文件gvcf，通过越来越多样本的joint-genotype可以使准确率越来越准确，其中shell脚本编写命令合并
    """

    def get_gvcf_for_combine(self):
        # step1: 生成gvcf，用于后面合并做群call joint-genotype
        return os.system(f"{self.gatk4} --java-options '-Xmx8G -Djava.io.tmpdir={self.tmp_dir}' HaplotypeCaller \
                            -R {self.ref_genome} --emit-ref-confidence GVCF -I {self.bam_file} -D {self.dbsnp} \
                            -L {self.exon_bed}   -O {self.out_no_suffix + '.gvcf'}")

    def combine_all_gvcf_file(self):
        # Path config
        combine_shell_path = self.WES_site + 'shell/' + 'combine_command.sh'
        # Run combine
        os.system(f"sh {combine_shell_path} {self.WES_site} {self.result_dir} {self.ref_genome}")

    def run_combine_command(self):
        shell_path = self.WES_site + 'shell/'
        os.system(f"sh {shell_path}combine2vcf.sh")

    def get_raw_vcf_no_combine(self):
        # get single sample:  /path/sample_name/sample_name.raw.vcf
        return os.system(f"{self.gatk4} --java-options '-Xmx8G -Djava.io.tmpdir={self.tmp_dir}' GenotypeGVCFs \
                          -R {self.ref_genome}  -V {self.out_no_suffix + '.gvcf'}  \
                          -L {self.exon_bed}   -O {self.out_no_suffix + '.raw.vcf'}")

    def get_raw_vcf_combine(self):
        # Path config
        # get combine sample:  /path/final.raw.vcf
        final_combine_g_vcf_path = '/'.join(self.result_dir.split('/')[:-1]) + '/final_combine.g.vcf'
        final_raw_vcf_path = '/'.join(self.result_dir.split('/')[:-1]) + '/final.raw.vcf'
        return os.system(f"{self.gatk4} --java-options '-Xmx8G -Djava.io.tmpdir={self.tmp_dir}' GenotypeGVCFs \
                          -R {self.ref_genome}  -V {final_combine_g_vcf_path}  -L {self.exon_bed} \
                          -O {final_raw_vcf_path}")


if __name__ == '__main__':
    parser = OptionParser(usage='%prog [-h]', version='%prog v1.0', description='GATK Mutant detection')
    parser.add_option("--b", "--bam_input", dest='bam_input', default='na', type=str, help="The BQSR bam file")
    parser.add_option("--o", "--output", dest="result_dir", type=str, help="The result path")
    parser.add_option("--g", "--genome_version", dest="genome_version", default='hg38', help="The ref genome version")
    parser.add_option("--m", "--method", dest="method", default='1', type=int, help="The Mutant detection opt 1 or 2 ")
    parser.add_option("--c", "--combine_mode", dest="combine", default='n', type=str,
                      help="y means yes or n means no, method == 1 will pass")
    options, args = parser.parse_args()

    VariantCheck(bam_input=options.bam_input,
                 result_dir=options.result_dir,
                 genome_version=options.genome_version,
                 method=options.method,
                 combine=options.combine)
