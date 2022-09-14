#!/usr/bin
annotate_varitation_pl=$1
genome_version=$2
humandb_dir=$3

# downloading human database
#command example: nohup sh ./dbdownl.sh /ifs1/software/analysis/annovar/annotate_variation.pl hg38 /ifs1/home/luohaosen/data/database/humandb/>./db.log 2>&1 &
#perl $annotate_varitation_pl -buildver $genome_version -downdb -webfrom annovar refGene $humandb_dir
#perl $annotate_varitation_pl --buildver $genome_version --downdb esp6500siv2_all --webfrom annovar $humandb_dir
#perl $annotate_varitation_pl --buildver $genome_version --downdb cytoBand $humandb_dir
#perl $annotate_varitation_pl --buildver $genome_version --downdb genomicSuperDups $humandb_dir
#perl $annotate_varitation_pl --buildver $genome_version --downdb gwascatalog $humandb_dir
#perl $annotate_varitation_pl --buildver $genome_version --downdb ljb26_all --webfrom annovar $humandb_dir
perl $annotate_varitation_pl --buildver $genome_version --downdb esp6500siv2_ea --webfrom annovar $humandb_dir
#perl $annotate_varitation_pl --buildver $genome_version --downdb 1000g2015aug $humandb_dir
#perl $annotate_varitation_pl --buildver $genome_version --downdb avsift -webfrom annovar $humandb_dir
#perl $annotate_varitation_pl --buildver $genome_version --downdb snp138 $humandb_dir
#perl $annotate_varitation_pl --buildver $genome_version --downdb phastConsElements46way $humandb_dir
#perl $annotate_varitation_pl --buildver $genome_version --downdb tfbs $humandb_dir
