=====================
Solr search transform
=====================


Configuration
-------------

You can configure the service with the following environment variables:

.. list-table::
   :header-rows: 1
   :widths: 10, 50, 30, 10

   * - Variable
     - Description
     - Default
     - Req

   * - ``SOLR_URL``
     - The SOLR URL to connect to. Note that the URL must be *encoded*.
     - ``http://localhost:8983/solr``
     -

   * - ``FILTER``
     - A search filter to apply for all queries. This must be a dictionary with field keys and term values.
     - ``{}``
     -

   * - ``SEARCH_FIELD``
     - The field to search in.
     - ``"text"``
     -

   * - ``RETURN_FIELDS``
     - JSON string array containing the document fields to return. If empty then return all fields.
     - ``[]``
     -

    
Example
-------

Before you run the service you have to have `Apache Solr <http://lucene.apache.org/solr/>`_ running and populated with data.


Add documents
^^^^^^^^^^^^^

This ``curl`` command posts three documents to the Solr server.

::

   curl -X POST -H 'Content-Type: application/json' 'http://localhost:8983/solr/collection1/update/json/docs?overwrite=true&commit=true' --data-binary '
   [
      {
        "id": "fox_brown",
        "url": "http://example.org/fox_brown",
        "text": "The quick brown fox jumps over the lazy dog",
        "labels": ["doc", "animal", "fox"]
      },
      {
        "id": "fox_yellow",
        "url": "http://example.org/fox_yellow",
        "text": "The quick yellow fox jumps over the lazy dog",
        "labels": ["doc", "animal", "fox"]
      },
      {
        "id": "ipsum",
        "url": "http://example.org/ipsum",
        "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
        "labels": ["doc", "latin"]
      }      
    ]'

Delete documents
^^^^^^^^^^^^^^^^

If you later need to delete all the documents in Solr you can issue the following ``curl`` command.

::

   curl 'http://localhost:8983/solr/collection1/update?commit=true' -H "Content-Type: text/xml" --data-binary '<delete><query>*:*</query></delete>'

Start the service
^^^^^^^^^^^^^^^^^

Start the service like this.

::

   $ FILTER='{"labels": "doc"}' RETURN_FIELDS='["id", "url"]' python3 service/service.py
   * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
   * Restarting with fsevents reloader
   * Debugger is active!
   * Debugger PIN: 206-748-648

     
Try the service
^^^^^^^^^^^^^^^

Now that Solr and the search transform service is running we can try it out. This example posts two query documents that each searches for some terms. As you can see from the output the ``"a"`` query returned two result documents while ``"b"`` returned just one result document.

::

    $ curl -s -X POST -H "Content-type: application/json" http://localhost:5000/search --data-binary '
    [
        {"_id": "a", "terms": ["brown", "yellow"]},
        {"_id": "b", "terms": ["lorem ipsum"], "payload": {"metadata": 123}}
    ]'|jq .
    [
      {
        "_id": "a",
        "result": [
          {
            "id": "fox_brown",
            "url": "http://example.org/fox_brown",
            "score": 0.12422675
          },
          {
            "id": "fox_yellow",
            "url": "http://example.org/fox_yellow",
            "score": 0.12422675
          }
        ]
      },
      {
        "_id": "b",
        "result": [
          {
            "id": "ipsum",
            "url": "http://example.org/ipsum",
            "score": 0.70273256
          }
        ],
        "payload": {
          "metadata": 123
        }
      }
    ]
    
Search terms are specified in the ``"terms"`` property. This property must be a list of strings. The ``"payload"`` property is optional, but if it is specified then it is copied onto the result document.
