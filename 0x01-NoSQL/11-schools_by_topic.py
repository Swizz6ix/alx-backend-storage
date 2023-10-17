#!/usr/bin/env python3
"""
A script that returns the list of school having a specific topic
"""


def schools_by_topic(mongo_collection, topic):
    """
    A function that returns the list of school having a specific topic
    mongo_collection will be the pymongo collection object
    """
    topic_filter = {
        'topics': {
            '$elemMatch': {
                '$eq': topic,
            },
        },
    }
    return [doc for doc in mongo_collection.find(topic_filter)]
