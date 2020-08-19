import argparse
import logging
import pickle

import pandas as pd
import torch

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from common import PROTOCOLS_FILE_PATH, OUTPUT_FORMATS, load_final_pipe, _write_json_contents

DEFAULT_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

DATA_DIR = 'data'
BASE_MODEL_DIR = os.path.join(DATA_DIR, 'text_summarization_models')
SUMMARY_MODELS = ['facebook/bart-large-cnn',
                  'distillbart_cnn_protocols',
                  'distillbart_xsum_protocols']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]

def trim_batch(input_ids, pad_token_id, attention_mask=None):
    """Remove columns that are populated exclusively by pad_token_id"""
    keep_column_mask = input_ids.ne(pad_token_id).any(dim=0)
    if attention_mask is None:
        return input_ids[:, keep_column_mask]
    else:
        return (input_ids[:, keep_column_mask], attention_mask[:, keep_column_mask])

def get_model_predictions(model, tokenizer, x):
    return [_predict(model, tokenizer, doc) for doc in x]

def _predict(model, tokenizer, doc):
    batch = tokenizer(doc, return_tensors="pt", truncation=True, padding="max_length").to(DEFAULT_DEVICE)
    input_ids, attention_mask = trim_batch(**batch, pad_token_id=tokenizer.pad_token_id)
    summaries = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        decoder_start_token_id=None
    )
    dec = tokenizer.batch_decode(summaries, skip_special_tokens=True, clean_up_tokenization_spaces=False)
    return dec[0]

def compute_summaries(protocols, model_name):
    model_path = name if 'distillbart' not in model_name \
                      else os.path.join(os.path.join(BASE_MODEL_DIR, model_name), 'best_tfmr')
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(DEFAULT_DEVICE)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    return get_model_predictions(model, tokenizer, protocols)

def show_summary_results(protocols_df, protocols, summaries, output, format):
    if format in RDF_FORMATS:
        show_protocols_graph_summaries(protocols_df, protocols, summaries, format, out_file)
    elif format == 'csv':
        show_protocols_csv_summaries(protocols_df, protocols, summaries, out_file)
    else:
        show_protocols_json_summaries(protocols_df, protocols, summaries, out_file)

def create_protocols_summary_graph(protocols_df, protocols, summaries):
    g = Graph()
    g.bind('edma', EDMA)
    g.bind('itsrdf', ITSRDF)
    g.bind('nif', NIF)
    collection_element = URIRef(f"{EDMA}{joblib.hash(protocols_df)}")
    g.add((collection_element, RDF.type, NIF.ContextCollection))
    for idx, summary in enumerate(summaries):
        text = protocols[idx]
        protocols_row = protocols_df.loc[idx]
        pr_id = protocols_row['pr_id']
        uri = f"https://bio-protocol.org/{pr_id}"

        context_element = URIRef(f"{EDMA}{pr_id}")
        text_element = Literal(text)
        g.add((context_element, NIF.isString, text_element))
        g.add((context_element, NIF.sourceURL, URIRef(uri)))
        g.add((context_element, NIF.predominantLanguage, Literal('en')))

        summary_element = BNode()
        g.add((summary_element, RDF.type, NIF.Context))
        g.add((summary_element, NIF.isString, summary))
        g.add((context_element, NIF.inter, summary_element))
        g.add((collection_element, NIF.hasContext, context_element))
    return g

def load_final_pipe():
    import string
    import en_core_sci_lg
    from collections import Counter
    from tqdm import tqdm

    en_core_sci_lg.load()
    return load_object(FINAL_PIPE_FILE_PATH)

def show_protocols_csv_results(protocols_df, protocols, summaries, out_file):
    fieldnames = ['protocol_id', 'summary']
    if out_file is not None:
        with open(out_file, 'w', encoding='utf-8') as f:
            csvwriter = csv.DictWriter(f, fieldnames=fieldnames)
            _write_csv_contents(csvwriter, protocols_df, protocols, topics)
    else:
        csvwriter = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        _write_csv_contents(csvwriter, protocols_df, protocols, topics)

def show_protocols_graph_summaries(protocols_df, protocols, summaries, format, out_file):
    g = create_protocols_summary_graph(protocols_df, protocols, summaries)
    if out_file is not None:
        g.serialize(destination=out_file, format=format)
    else:
        print(g.serialize(format=format).decode("utf-8"))

def show_protocols_json_results(protocols_df, protocols, summaries, out_file):
    res = {}
    for idx, summary in enumerate(summaries):
        protocol_row = protocols_df.loc[idx]
        protocol_id = protocol_row['pr_id']
        protocol_title = protocol_row['title']
        protocol_authors = protocol_row['authors'].split('|')
        source_url = f"https://bio-protocol.org/{protocol_id}"
        res[str(protocol_id)] = {
            'source_url': source_url,
            'authors': protocol_authors,
            'title': protocol_title,
            'summary': summary
        }
    _write_json_contents(res, out_file)

def _write_csv_contents(csvwriter, protocols_df, protocols, summaries):
    csvwriter.writeheader()
    for idx, summary in enumerate(summaries):
        protocol_id = protocols_df.loc[idx]['pr_id']
        csvwriter.writerow({
            'protocol_id': protocol_id,
            'summary': summary
        })

def parseargs():
    parser = argparse.ArgumentParser(description="Run predictions for the protocol track dataset")
    parser.add_argument('-m', '--model', choices=SUMMARY_MODELS, help="Name of the file where the results will be saved. " +
        "If no output file is specified, results will be written to the console instead.",
        nargs='?', default=None)
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
    summaries = compute_summaries(protocols, args.model)final_pipe.transform(protocols)
    logger.info('Writting results...')
    show_summary_results(protocols_df, protocols, summaries, args.output, args.format)

if __name__ == '__main__':
    args = parseargs()
    exit(main(args))
