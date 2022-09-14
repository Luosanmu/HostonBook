source=$1
align_mode=$2
threading=$3
sample=$4
result_path=$5
genome_version=$6
min_quality=$7
method=$8
combine_vcf_mode=$9
qc_way=${10}

sample_path_no_suffix=${sample%%.*gz}
sample_prefix=${sample_path_no_suffix##*/}
output_no_suffix=${result_path}${sample_prefix}/${sample_prefix}

# 过滤低质量序列，bwa比对得到bam文件, 做初步统计
python "$source"script/filter_align_statistics.py --m "$align_mode" --t "$threading" --i "$sample" --o "$result_path"  --g "$genome_version" --q "$min_quality"

# 外显子覆盖度，PCR重复序列标记，碱基质量校正
python "$source"script/correct_base.py --b "$output_no_suffix".bam --o "$result_path" --g "$genome_version"

# haplotypecaller变异位点检测
python "$source"script/variation_check.py --b "$output_no_suffix".MarkDuplicates.BQSR.bam --o "$result_path" --g "$genome_version" --m "$method" --c  "$combine_vcf_mode"

if [ "$combine_vcf_mode" == 'y' ];then
  vcf_path=${result_path}final.raw.vcf
elif [ "$combine_vcf_mode" == 'n' ];then
  vcf_path=${output_no_suffix}.raw.vcf
else
  echo "You should opt combine gvcf mode, y (yes) or n (no)";
fi
## anno
python "$source"script/snp_anno.py --v "$vcf_path" --o "$result_path" --g "$genome_version" --q "$qc_way"


# del middle file
#rm "$output_no_suffix".clean.fq.gz
#rm "$output_no_suffix".bam*
#rm "$output_no_suffix".rmdup.bam*
#rm "$output_no_suffix".MarkDuplicates*
#rm "$output_no_suffix".snp.vcf*
#rm "$output_no_suffix".indel.vcf*
rm "$output_no_suffix".snp.filter.vcf*
rm "$output_no_suffix".indel.filter.vcf*
rm "$output_no_suffix"_snp_anno*
rm "$output_no_suffix"_indel_anno*
