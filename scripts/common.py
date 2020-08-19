import csv
import joblib
import json
import os
import requests
import sys
import time

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

from herc_common.utils import add_text_topics_to_graph, load_object, EDMA, ITSRDF, NIF


BASE_URL = "https://bio-protocol.org/"
RESULTS_DIR = 'results'
NOTEBOOK_2_RESULTS_DIR = os.path.join(RESULTS_DIR, '2_data_exploration')
NOTEBOOK_6_RESULTS_DIR = os.path.join(RESULTS_DIR, '6_complete_system')

PROTOCOLS_FILE_PATH = os.path.join(NOTEBOOK_2_RESULTS_DIR, 'protocols_dataframe.pkl')
FINAL_PIPE_FILE_PATH = os.path.join(NOTEBOOK_6_RESULTS_DIR, 'final_pipe.pkl')

RDF_FORMATS = {'json-ld', 'n3', 'xml', 'turtle'}
OUTPUT_FORMATS = RDF_FORMATS | {'csv', 'json'}


class BioProtocolScrapper():
    def __init__(self, output_dir, throttle_time=.5,
                 username=None, password=None):
        self.output_dir = output_dir
        self.throttle_time = throttle_time
        if username and password:
            self.login(username, password)

    def fetch_urls(self, url_list):
        res = {}
        for url in url_list:
            id, content = self.fetch_url(url)
            res[id] = content
            time.sleep(self.throttle_time)

    def fetch_url(self, url):
        id = url.split('/')[-1] if '/' in url else url
        return id, response.text

    def _login(self, user, password):
        payload = {'txtEmail': user, 'txtPassword': password}
        url = f'{BASE_URL}/ifrlogin.aspx/?sign=in&p=4'
        requests.post(url, data=payload)

def create_protocols_graph(protocols_df, protocols, topics):
    g = Graph()
    g.bind('edma', EDMA)
    g.bind('itsrdf', ITSRDF)
    g.bind('nif', NIF)
    collection_element = URIRef(f"{EDMA}{joblib.hash(protocols_df)}")
    g.add((collection_element, RDF.type, NIF.ContextCollection))
    for idx, protocol_topics in enumerate(topics):
        text = protocols[idx]
        protocols_row = protocols_df.loc[idx]
        pr_id = protocols_row['pr_id']
        uri = f"https://bio-protocol.org/{pr_id}"
        context_element = add_text_topics_to_graph(uri, pr_id, text, protocol_topics, g)
        g.add((collection_element, NIF.hasContext, context_element))
    return g

def load_final_pipe():
    import string
    import en_core_sci_lg
    from collections import Counter
    from tqdm import tqdm

    en_core_sci_lg.load()
    return load_object(FINAL_PIPE_FILE_PATH)

def show_protocols_csv_results(protocols_df, protocols, topics, out_file):
    fieldnames = ['protocol_id', 'topics']
    if out_file is not None:
        with open(out_file, 'w', encoding='utf-8') as f:
            csvwriter = csv.DictWriter(f, fieldnames=fieldnames)
            _write_csv_contents(csvwriter, protocols_df, protocols, topics)
    else:
        csvwriter = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        _write_csv_contents(csvwriter, protocols_df, protocols, topics)

def show_protocols_graph_results(protocols_df, protocols, topics, format, out_file):
    g = create_protocols_graph(protocols_df, protocols, topics)
    if out_file is not None:
        g.serialize(destination=out_file, format=format)
    else:
        print(g.serialize(format=format).decode("utf-8"))

def show_protocols_json_results(protocols_df, protocols, topics, out_file):
    res = {}
    for idx, protocol_topics in enumerate(topics):
        protocol_topics = [t[0] for t in protocol_topics]
        protocol_row = protocols_df.loc[idx]
        protocol_id = protocol_row['pr_id']
        protocol_title = protocol_row['title']
        protocol_authors = protocol_row['authors'].split('|')
        source_url = f"https://bio-protocol.org/{protocol_id}"
        res[str(protocol_id)] = {
            'source_url': source_url,
            'authors': protocol_authors,
            'title': protocol_title,
            'topics': [{
                'labels': t.labels,
                'external_ids': t.uris,
                'descriptions': t.descs,
                'score': t.score
            } for t in protocol_topics]
        }
    _write_json_contents(res, out_file)

def show_results(protocols_df, protocols, topics, out_file, format):
    if format in RDF_FORMATS:
        show_protocols_graph_results(protocols_df, protocols, topics, format, out_file)
    elif format == 'csv':
        show_protocols_csv_results(protocols_df, protocols, topics, out_file)
    else:
        show_protocols_json_results(protocols_df, protocols, topics, out_file)


def _write_csv_contents(csvwriter, protocols_df, protocols, topics):
    csvwriter.writeheader()
    for idx, protocol_topics in enumerate(topics):
        protocol_topics = [t[0] for t in protocol_topics]
        protocol_id = protocols_df.loc[idx]['pr_id']
        csvwriter.writerow({
            'protocol_id': protocol_id,
            'topics': ' - '.join([str(t) for t in protocol_topics])
        })

def _write_json_contents(res, out_file):
    if out_file is not None:
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(res, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(res, indent=2, ensure_ascii=False))
