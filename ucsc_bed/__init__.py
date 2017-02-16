#!/usr/bin/env python3
import argparse
import ftplib
import gzip
import functools
import io

import pandas as pd


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('reference',
                        help='The version of the reference genome to use. Must start with "hg", e.g. "hg38"')
    parser.add_argument('--limit', '-l', type=int, required=False,
                        help='The maximum number of transcripts to use as a data source (defaults to all)')
    parser.add_argument('--email', '-e', required=False, help='The email address to use when logging onto the ftp site')
    parser.add_argument('--method', '-m', choices=['ftp', 'sql'],
                        help='The method to use to obtain the transcript information', default='sql')
    parser.add_argument('--strip-alt', '-a', required=False,
                        help='Strip the exons on alternative contigs (e.g. from HG38 onwards)')

    return parser.parse_args()


def download_table(reference, email):
    # Download the zip file into memory
    file = io.BytesIO()
    ftp = ftplib.FTP('hgdownload.cse.ucsc.edu', user='anonymous', passwd=email)
    ftp.retrbinary(f'RETR goldenPath/{reference}/database/refFlat.txt.gz', file.write)

    # Rewind the file
    file.seek(0)

    # Return an unzipped stream
    gz = gzip.GzipFile(fileobj=file)

    df = (pd.read_csv(gz, sep='\t',
                      names=["geneName", "name", "chrom", "strand", "txStart", "txEnd", "cdsStart", "cdsEnd",
                             "exonCount", "exonStarts", "exonEnds"])
          .ix[:, ['chrom', 'exonStarts', 'exonEnds', 'geneName']]
          )

    return df


def query_table(reference, limit):
    # First, read the file in as a data frame
    query_str = 'SELECT chrom, exonStarts, exonEnds, geneName from refFlat'

    if limit:
        query_str += f'LIMIT {limit};'
    else:
        query_str += ';'

    df = pd.read_sql(query_str,
                     con=f'mysql+mysqldb://genome@genome-mysql.cse.ucsc.edu/{reference}?charset=utf8&use_unicode=1')
    df['exonStarts'] = df['exonStarts'].str.decode('utf-8')
    df['exonEnds'] = df['exonEnds'].str.decode('utf-8')
    return df


def convert_to_bed(left, strip_alt):
    # TODO: Implement strip_alt

    # Split the start and end of the exons into separate series each
    right_components = [
        left[col]
            .str
            .split(',', expand=True)
            .stack()
            .replace('', pd.np.nan)
            .dropna()
            .astype(pd.np.int32)
            .to_frame()
            .rename(columns={0: col[0:-1]})
        for col in ['exonStarts', 'exonEnds']
        ]

    # Merge these two series into one data frame based on both of their indices, then drop the index that indicates
    # the index of the exon for this transcript (because we don't need it anymore)
    right = (
        functools
            .reduce(lambda a, b: a.join(b) if a is not None else b, right_components)
            .reset_index(level=1, drop=True)
    )

    # Merge the exon data frame with the main data frame on the index that indicates the original row number
    df = left.ix[:, ['chrom', 'geneName']].merge(right, left_index=True, right_index=True).sort_values(
        by=['chrom', 'exonStart', 'exonEnd'])

    return df.to_csv(sep='\t', columns=['chrom', 'exonStart', 'exonEnd', 'geneName'], index=False, header=False)


def generate_bed(reference, method, limit=None, email=None, strip_alt=False):
    """
    Python entry point. Takes a reference string and an email and returns the bed file as a string
    :param reference: The genome reference to use to generate a BED file. Must start with "hg", e.g. "hg38"
    """

    if method == 'sql':
        df = query_table(reference, limit)
    else:
        df = download_table(reference, email)
    return convert_to_bed(df, strip_alt)


def main():
    """
    Command line entry point. Has no python parameters, so parses its parameters from argv
    """
    args = get_args()
    bed = generate_bed(**args)
    print(bed)


if __name__ == '__main__':
    main()
