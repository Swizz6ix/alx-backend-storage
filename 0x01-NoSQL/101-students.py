#!/usr/bin/env python3
"""
A script that returns all students sorted by average
"""


def top_students(mongo_collection):
    """
    A function that returns students sorted by average
    mongo_collection will be the pymongo collection object
    The top must be ordered
    """
    students = mongo_collection.aggregate(
        [
            {
                '$project': {
                    '_id': 1,
                    'name': 1,
                    'averageScore': {
                        '$avg': {
                            '$avg': '$topics.score',
                        },
                    },
                    'topics': 1,
                },
            },
            {
                '$sort': {
                    'averageScore': -1
                },
            },
        ]
    )
    return students
