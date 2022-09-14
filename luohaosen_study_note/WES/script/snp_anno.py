# Time: 22/9/7 23:31
# Author: Haosen Luo
# @File: variant_check.py
import os
import configparser
from optparse import OptionParser

BIN = os.path.dirname(__file__) + '/'
file_config = configparser.ConfigParser()
file_config.read(BIN + 'config.ini')


class VariantAnno(object):
    def __init__(self, vcf_input, result_dir, genome_version='hg38', qc_way=2):
        if vcf_input.endswith('.raw.vcf'):
            # raw_vcf_name = /path/final.raw.vcf  |  /path/result/sample_name.raw.vcf
            self.raw_vcf = vcf_input
        else:
            raise Exception("The input path is not '/path/sample_name.MarkDuplicates.BQSR.bam'")
        self.out_no_suffix = self.raw_vcf.split('.')[0]
        self.result_dir = result_dir
        # 用于存放java缓存tmp_dir
        self.tmp_dir = '/'.join(result_dir.split('/')[:-2]) + '/java_tmp/'
        self.genome = genome_version
        self.qc_way = qc_way
        # ev means 'exon_version' 是安捷伦外显子参考版本
        self.ev = '_'.join((self.genome, 'v8'))
        self.exon_bed = file_config['Exon_bam'][self.ev]
        self.ref_genome = file_config['Reference'][self.genome]
        # Anno database parser
        self.dbsnp = file_config['Annotation']['_'.join((self.genome, 'dbsnp'))]
        self.hapmap = file_config['Annotation']['_'.join((self.genome, 'hapmap'))]
        self.omni = file_config['Annotation']['_'.join((self.genome, 'omni'))]
        self.phase = file_config['Annotation']['_'.join((self.genome, 'phase'))]
        self.db_dir = file_config['Annotation']['_'.join((self.genome, 'humandb', 'path'))]
        # Software parameter
        self.gatk4 = file_config['Software']['gatk4']
        self.annovar_covert = file_config['Annovar']['convert']
        self.annovar_table = file_config['Annovar']['table']
        # Filter
        self.qc_filter(qc_way)
        # Anno
        # self.snp_annotation()
        # self.indel_annotation()
        self.merge_annotation()

    # 使用指标过滤法跑通，不使用VQSR的原因是无法界定数量达到多少才能称为”足够多“
    def qc_filter(self, qc_way):
        if qc_way == 1:
            """
            GATK VQSR, 全基因组分析或多个样本的全外显子组分析适合用此方法
            需要一个已知变异集作为训练质控模型的真集。比如，Hapmap、OMNI，1000G和dbsnp
            新检测的结果中有足够多的变异，不然VQSR在进行模型训练的时候会因为可用的变异位点数目不足而无法进行
            """
            os.system(f"{self.gatk4} --java-options '-Xmx8G -Djava.io.tmpdir={self.tmp_dir}' VariantRecalibrator \
                        -R {self.ref_genome}  -V {self.raw_vcf} \
                        -resource hapmap,known=false,training=true,truth=true,prior=15.0:{self.hapmap} \
                        -resource omini,known=false,training=true,truth=false,prior=12.0:{self.omni} \
                        -resource 1000G,known=false,training=true,truth=false,prior=10.0:{self.phase} \
                        -resource dbsnp,known=true,training=false,truth=false,prior=6.0:{self.dbsnp} \
                        -an QD -an MQ -an MQRankSum -an ReadPosRankSum -an FS -an SOR -an DP -mode SNP \
                        -O {self.out_no_suffix + '.snps.recal.vcf'} \
                        --tranches-file {self.out_no_suffix + '.snps.tranches'}\
                        --rscript-file {self.out_no_suffix + '.snps.plots.R'} ")
            os.system(f"{self.gatk4}  ApplyRecalibration  -V {self.raw_vcf} \
                         -O {self.out_no_suffix + '.VQSR.vcf'} --recal-file {self.out_no_suffix + '.snps.recal.vcf'}\
                         --tranches-file {self.out_no_suffix + '.snps.tranches'}  -mode SNP")
        elif qc_way == 2:
            """
            指标过滤法
            QD:            变异质量值/覆盖深度
            FS:            通过Fisher检验的p-value转换而来的值，描述测序或者比对时对于只含有变异的read以及只含有参考序列
                                         碱基的read是否存在着明显的正负链特异性（Strand bias，或者说是差异性）
            SOR            对链特异（Strand bias）的一种描述
            MQ             所有比对至该位点上的read的比对质量值的均方根
            MQRankSum      
            ReadPosRankSum 
            """
            # select SNP
            os.system(f"{self.gatk4} SelectVariants -select-type SNP -V {self.raw_vcf} \
                         -O {self.out_no_suffix + '.snp.vcf'}")
            os.system(f"{self.gatk4} VariantFiltration -V {self.out_no_suffix + '.snp.vcf'}  --filter-expression \
                        'QD < 2.0 || MQ < 40.0 || FS > 60.0 || SOR > 3.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0'\
                          --filter-name 'PASS' -O {self.out_no_suffix + '.snp.filter.vcf'}")
            # select Indel
            os.system(f"{self.gatk4} SelectVariants -select-type INDEL -V {self.raw_vcf} \
                         -O {self.out_no_suffix + '.indel.vcf'}")
            os.system(f"{self.gatk4} VariantFiltration -V {self.out_no_suffix + '.indel.vcf'} --filter-expression \
                        'QD < 2.0 || FS > 200.0 || SOR > 10.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0' \
                        --filter-name 'PASS' -O {self.out_no_suffix + '.indel.filter.vcf'}")
            # merge snp and indel to filter.vcf
            os.system(f"{self.gatk4} MergeVcfs -I {self.out_no_suffix + '.snp.filter.vcf'} \
                         -I {self.out_no_suffix + '.indel.filter.vcf'} -O {self.out_no_suffix + '.filter.vcf'}")
        else:
            raise Exception("The qc way should input 1 or 2")

    """
    运行table_annovar.pl时需要保证annotate_variation.pl是可执行状态
    # chmod a+x annotate_variation.pl
    # chmod a+x table_annovar.pl
    """

    # def snp_annotation(self):
    #     # 转化 filter.vcf -> .avinput
    #     # snp filter -> snp avinput
    #     os.system(f"perl {self.annovar_covert} -format vcf4   {self.out_no_suffix + '.snp.filter.vcf'} > \
    #                  {self.out_no_suffix + '.snp.avinput'}")
    #     # snp avinput -> snp csv
    #     os.system(f"perl {self.annovar_table} {self.out_no_suffix + '.snp.avinput'} {self.db_dir} \
    #                 -buildver {self.genome} -out {self.out_no_suffix + '_snp_anno'} -remove \
    #                 -protocol refGene,cytoBand,genomicSuperDups,esp6500siv2_all -operation g,r,r,f -nastring . -csvout
    #                 ")
    #
    # def indel_annotation(self):
    #     # 转化 filter.vcf -> .avinput
    #     # indel filter -> indel avinput
    #     os.system(f"perl {self.annovar_covert} -format vcf4   {self.out_no_suffix + '.indel.filter.vcf'} > \
    #                  {self.out_no_suffix + '.indel.avinput'}")
    #     # indel avinput -> indel csv
    #     os.system(f"perl {self.annovar_table} {self.out_no_suffix + '.indel.avinput'} {self.db_dir} \
    #                 -buildver {self.genome} -out {self.out_no_suffix + '_indel_anno'} -remove \
    #                 -protocol refGene,cytoBand,genomicSuperDups,esp6500siv2_all -operation g,r,r,f -nastring . -csvout
    #                 ")

    def merge_annotation(self):
        # 转化 filter.vcf -> .avinput
        # indel filter -> indel avinput
        os.system(f"perl {self.annovar_covert} -format vcf4   {self.out_no_suffix + '.filter.vcf'} > \
                     {self.out_no_suffix + '.filter.avinput'}")
        # indel avinput -> indel csv
        os.system(f"perl {self.annovar_table} {self.out_no_suffix + '.filter.avinput'} {self.db_dir} \
                    -buildver {self.genome} -out {self.out_no_suffix + '_filter_anno'} -remove \
                    -protocol refGene,cytoBand,genomicSuperDups,esp6500siv2_all -operation g,r,r,f -nastring . -csvout")


if __name__ == '__main__':
    parser = OptionParser(usage='%prog [-h]', version='%prog v1.0', description='Filter raw vcf and Annotate variation')
    parser.add_option("--v", "--vcf_input", dest='vcf_input', default='na', type=str, help="The raw vcf file path")
    parser.add_option("--o", "--output", dest="result_dir", type=str, help="The result path")
    parser.add_option("--g", "--genome_version", dest="genome_version", default='hg38', help="The ref genome version")
    parser.add_option("--q", "--qc", dest="qc_way", default='2', type=int, help="The qc way of VQSR or Target")
    options, args = parser.parse_args()
    # running anno
    VariantAnno(vcf_input=options.vcf_input,
                result_dir=options.result_dir,
                genome_version=options.genome_version,
                qc_way=options.qc_way)
