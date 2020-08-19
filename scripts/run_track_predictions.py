import argparse
import logging
import pickle

import pandas as pd

from common import PROTOCOLS_FILE_PATH, OUTPUT_FORMATS, load_final_pipe, show_results


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parseargs():
    parser = argparse.ArgumentParser(description="Run predictions for the protocol track dataset")
    parser.add_argument('-f', '--format', choices=OUTPUT_FORMATS, help="Output format of the results. " +
        "If no output format is specified, results are returned in JSON by default.",
        nargs='?', default='json')
    parser.add_argument('-o', '--output', help="Name of the file where the results will be saved. " +
        "If no output file is specified, results will be written to the console instead.",
        nargs='?', default=None)
    return parser.parse_args()

def main(args):
    logger.info('Reading track dataset...')
    protocols_df = pd.read_pickle(PROTOCOLS_FILE_PATH)
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
