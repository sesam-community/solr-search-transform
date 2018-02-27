# -*- coding: utf-8 -*-
from flask import Flask, request, Response
from collections.abc import Mapping
import logging
import os
import json
import pysolr
import re

from werkzeug.exceptions import BadRequest

app = Flask (__name__)


ESCAPE_CHARS_RE = re.compile(r'(?<!\\)(?P<char>[&|+\-!(){}[\]^"~*?:])')

def solr_escape(value):
    return ESCAPE_CHARS_RE.sub(r'\\\g<char>', value)


@app.route('/search', methods=["POST"])
def search():
    entities = request.get_json()
    print(entities)
    if not isinstance(entities, list):
        return BadRequest("Payload must be JSON array of entities")

    for entity in entities:
        terms = entity.get("terms")
        if not isinstance(terms, list) or len(terms) == 0:
            return BadRequest("\"terms\" must be JSON array of string terms")

    search_filter = json.loads(os.environ.get("FILTER", "null"))
    fq = []
    if isinstance(search_filter, Mapping):
        for k, v in search_filter.items():
            fq.append(k + ":" + v)
        
    return_fields = json.loads(os.environ.get("RETURN_FIELDS", "[]"))
    if return_fields:
        fl = ",".join(return_fields) + " score"
    else:
        fl = "* score"

    qf = os.environ.get("SEARCH_FIELD", "text")
    
    def perform_search():
        yield b"["
        solr = pysolr.Solr(os.environ.get('SOLR_URL', 'http://localhost:8983/solr'), timeout=60)

        for ix, entity in enumerate(entities):
            if ix > 0:
                yield b", "
    
            terms = entity.get("terms")
            q = " OR ".join(['"' + solr_escape(t) + '"' for t in terms])
            q_args = {
                "defType": "edismax",
                "qf": qf,
                "fl": fl,
                "rows": 1000,
            }
            if fq:
                q_args["fq"] = fq
                
            qr = solr.search(q, **q_args)
            print("Q:", q, q_args, qr.hits, "hits")

            doc = {"_id": entity["_id"], "result": qr.docs}

            if "payload" in entity:
                doc["payload"] = entity["payload"]
                
            yield json.dumps(doc)
        yield b"]"

    return Response(response=perform_search(), status=200, mimetype='application/json')


if __name__ == '__main__':
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))

    logger = logging.getLogger('solr-search-transform')
    logger.addHandler(stdout_handler)
    logger.setLevel(logging.INFO)
    
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
