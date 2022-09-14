import os
from optparse import OptionParser
import configparser

BIN = os.path.dirname(__file__) + '/'
file_config = configparser.ConfigParser()
file_config.read(BIN + 'config.ini')


def combine_all_gvcf_file(result_dir, genome):
    ref_genome = file_config['Reference'][genome]
    # Path config
    shell_path = '/'.join(result_dir.split('/')[:-2]) + '/shell/'
    # Run combine
    return os.system(f"sh {shell_path + 'combine_command.sh'} {'/'.join(result_dir.split('/')[:-2]) + '/'} \
                      {result_dir} {ref_genome}")


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--o", "--output", dest="result_dir", type=str, help="result_dir")
    parser.add_option("--g", "--genome", dest="genome", help="The version of genome")
    options, args = parser.parse_args()
    combine_all_gvcf_file(result_dir=options.result_dir, genome=options.genome)
