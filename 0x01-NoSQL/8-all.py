#!/usr/bin/env python3
"""
A script that lists all documents in a collection
"""


def list_all(mongo_collection):
    """
    A function that returns a list of all documents in a collection
    it returns an empty list if there's no document in the collection
    """
    return [doc for doc in mongo_collection.find()]
