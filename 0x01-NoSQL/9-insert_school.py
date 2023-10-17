#!/usr/bin/env python3
"""
A script that describes a function that insert a new document in a collection 
"""


def insert_school(mongo_collection, **kwargs):
    """
    A function that insert a new document ina collection based on kwargs
    """
    result = mongo_collection.insert_one(kwargs)
    return result.inserted_id
