import argparse
import logging
import pickle
import os
import re
import sys

import pandas as pd

from common import OUTPUT_FORMATS, load_final_pipe, show_results, BioProtocolScrapper

parentdir = os.path.dirname('..')
sys.path.insert(0,parentdir)
from src.data_reader import parse_protocol


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def join_procedure_steps(procedure):
    return ' '.join(procedure.split('|'))

def clean(procedure):
    merged_procedure = join_procedure_steps(procedure)
    return re.sub('\s+', ' ', merged_procedure).strip()

def load_protocols_df(input, is_file, token):
    if is_file:
        with open(input, 'r', encoding='utf-8') as f:
            protocols_urls = [line.rstrip('\n') for line in f]
    else:
        protocols_urls = [input]
    scrapper = BioProtocolScrapper(PROTOCOLS_DIR)
    protocols_data = scrapper.fetch_urls(protocols_urls)
    parsed_protocols = [parse_protocol(pr_content, pr_id)
                        for pr_content, pr_id in protocols_data.items()]
    df = pd.DataFrame([repo.to_dict() for repo in parsed_protocols])
    df['full_text'] = df['title'] + '. ' + df['abstract'] + '. ' + df['procedure'] + '. ' + df['background']
    df['full_text_no_abstract'] = df['title'] + '. ' + df['procedure'] + '. ' + df['background']
    df['full_text_cleaned'] = df['full_text'].apply(lambda x: clean(x))
    df['full_text_no_abstract_cleaned'] =df['full_text_no_abstract'].apply(lambda x: clean(x))
    return df

def parseargs():
    parser = argparse.ArgumentParser(description="Run predictions for the protocols track dataset")
    parser.add_argument('input', type=str, help="URL of the protocol to extract " +
        "the topics from. If the --file flag is set, file with the urls of the protocols")
    parser.add_argument('--username', type=str, required=True, help="Bioprotocols username used to fetch information about " +
        "the input protocols before the topic extraction steps.")
    parser.add_argument('--password', type=str, required=True, help="Bioprotocols password used to fetch information about " +
        "the input protocols before the topic extraction steps.")
    parser.add_argument('--isFile', action='store_true', default=False, help="If present, this flag " +
        "indicates that the input passed to the script is a file with the urls of each protocol " +
        "delimited by newlines.")
    parser.add_argument('-f', '--format', choices=OUTPUT_FORMATS, help="Output format of the results. " +
        "If no output format is specified, results are returned in JSON by default.",
        nargs='?', default='json')
    parser.add_argument('-o', '--output', help="Name of the file where the results will be saved. " +
        "If no output file is specified, results will be written to the console instead.",
        nargs='?', default=None)
    return parser.parse_args()

def main(args):
    logger.info('Loading protocol data...')
    protocols_df = load_protocols_df(args.input, args.isFile, args.token)
    logger.info('Loading topic extraction model...')
    final_pipe = load_final_pipe()
    protocols = protocols_df['full_text_cleaned'].values
    logger.info('Predicting topics...')
    topics = final_pipe.transform(protocols)
    logger.info('Writting results...')
    show_results(protocols_df, protocols, topics, args.output, args.format)

if __name__ == '__main__':
    args = parseargs()
    exit(main(args))
