#!/usr/bin/env python3
"""
A script that changes all topics of a school document
"""


def update_topics(mongo_collection, name, topics):
    """
    A function that changes all topics of a school document base on thr name
    """
    mongo_collection.update_many(
        {'name': name},
        {'$set': {'topics': topics}}
    )
