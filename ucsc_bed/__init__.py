#!/usr/bin/env python3
import argparse
import pandas as pd
import ftplib
import typing
import gzip
import functools
import io


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('reference')
    parser.add_argument('--email', '-e', required=True)

    return parser.parse_args()


def download_table(reference, email):
    # Download the zip file into memory
    file = io.BytesIO()
    ftp = ftplib.FTP('hgdownload.cse.ucsc.edu', user='anonymous', passwd=email)
    ftp.retrbinary(f'RETR goldenPath/{reference}/database/refFlat.txt.gz', file.write)

    # Rewind the file
    file.seek(0)

    # Return an unzipped stream
    return gzip.GzipFile(fileobj=file)


def transform_table(table: typing.TextIO):
    # First, read the file in as a data frame
    left = pd.read_csv(table, sep='\t',
                       names=["geneName", "name", "chrom", "strand", "txStart", "txEnd", "cdsStart", "cdsEnd",
                              "exonCount", "exonStarts", "exonEnds"])

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
    left = left.merge(right, left_index=True, right_index=True)

    # Extract the relevant columns
    df = left.ix[:, ['chrom', 'exonStart', 'exonEnd', 'geneName']].sort(['chrom', 'exonStart', 'exonEnd'])

    return df.to_csv(sep='\t', index=False, header=False)


def main():
    args = get_args()
    table = download_table(args.reference, args.email)
    return transform_table(table)


if __name__ == '__main__':
    print(main())
