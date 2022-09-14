# Time: 22/09/13
# Author: Haosen Luo
# Filename: statistics_variation.py
import os
from optparse import OptionParser
import configparser
import pandas as pd

BIN = os.path.dirname(__file__)
file_config = configparser.ConfigParser()
file_config.read(BIN + 'config.ini')


class StatisticsVar(object):
    def __init__(self, csv_path, result_dir):
        self.csv = csv_path
        if csv_path.endswith('.vcf'):
            self.output_no_suffix = self.csv.split('.')[0]
            self.sample_name = self.output_no_suffix.split('/')[-1]
        self.result_dir = result_dir

    def read_csv_file(self, csv_path):
        return pd.read_table(self.csv, sep='\t', skiprows='',)

    def merge_all_sample_csv(self):
        for single_sample in os.listdir(self.result_dir):
            for single_csv in os.listdir(single_sample):
                df = self.read_csv_file(single_csv)


def main():
    ...


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--i", "--input", dest="csv_path", default='na', help="The vcf to run")
    parser.add_option("--o", "--output", dest="result_dir", default='na', help="The result directory")
    options, args = parser.parse_args()
    if options.vcf_path == 'na':
        main()
    else:
        StatisticsVar(csv_path=options.csv_path, result_dir=options.result_dir)
