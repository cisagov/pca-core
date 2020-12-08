__all__ = [
    "connect_from_config",
    "db_from_connection",
    "db_from_config",
    "id_expand",
    "ensure_indices",
]

import sys
import copy
from pymongo import MongoClient
from pymodm import MongoModel, fields, connect
from pca.config import Config


def connect_from_config(config_section=None):
    config = Config(config_section)
    connect(config.db_uri, tz_aware=True)
    return True


def db_from_connection(uri, name):
    con = MongoClient(host=uri, tz_aware=True)
    db = con[name]
    return db


def db_from_config(config_section=None):
    config = Config(config_section)
    return db_from_connection(config.db_uri, config.db_name)


def id_expand(results):
    """Extract items from aggregation grouping _id dictionary and insert into outer results"""
    for result in results:
        if "_id" not in result:
            continue
        _id = result["_id"]
        if type(_id) == dict:
            for (k, v) in _id.items():
                if k == "port":  # map-reduce ints become floats
                    v = int(v)
                result[k] = v
            del result["_id"]


def combine_results(d, results, envelope=None):
    """updates dict with pipeline results"""
    if len(results) == 0:
        return
    results = copy.copy(results)  # don't want to modifiy the results input
    the_goods = results[0]
    del the_goods["_id"]
    if envelope:
        the_goods = {envelope: the_goods}
    d.update(the_goods)


def run_pipeline(pipeline_collection_tuple, db):
    """Run an aggregation using a pipeline, collection tuple like those provided
       in the queries module."""
    (pipeline, collection) = pipeline_collection_tuple
    try:
        results = db[collection].aggregate(pipeline, allowDiskUse=True)
    except OperationFailure as e:
        if e.details["code"] == 16389:
            e.args += (
                "To avoid this error consider calling run_pipeline_cursor instead.",
            )
        raise e
    return results["result"]


def run_pipeline_cursor(pipeline_collection_tuple, db):
    """Like run_pipeline but uses a cursor to access results larger than the max
       MongoDB size."""
    (pipeline, collection) = pipeline_collection_tuple
    cursor = db[collection].aggregate(pipeline, allowDiskUse=True, cursor={})
    results = []
    for doc in cursor:
        results.append(doc)
    return results


def ensure_indices(db, foreground=False):
    background = not foreground
    if background:
        print("Ensuring indices for all collection in background.", file=sys.stderr)
    else:
        print("Ensuring indices for all collection in FOREGROUND.", file=sys.stderr)

    # possibly delving too greedily and too deep
    for class_name, clazz in db.connection._registered_documents.items():
        print >>sys.stderr, "Ensuring indices for %s:" % class_name
        indices = db[class_name].get_indices()
        if not indices:
            continue
        for name, spec, unique, sparse in indices:
            print(
                "\t%s:\tunique=%s\tsparse=%s\t%s ..." % (name, unique, sparse, spec),
                end=" ",
                file=sys.stderr,
            )
            db[class_name].collection.ensure_index(
                spec, name=name, background=background, unique=unique, sparse=sparse
            )
            print(" Done", file=sys.stderr)
