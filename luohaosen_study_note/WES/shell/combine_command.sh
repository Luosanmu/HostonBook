source=$1
result_dir=$2
ref_genome=$3

# Find gvcf
find "$result_dir" -name "*.gvcf" > "$source"input_list

# Write script process
echo -e "gatk CombineGVCFs\\" > ${source}shell/combine2vcf.sh

echo -e " -R ${ref_genome}\\" >> ${source}shell/combine2vcf.sh

for i in $( cat "$source"input_list )
do
  echo -e " -V ${i}\\">> ${source}shell/combine2vcf.sh;
done

echo " -O ${result_dir}final_combine.g.vcf" >> "$source"shell/combine2vcf.sh
