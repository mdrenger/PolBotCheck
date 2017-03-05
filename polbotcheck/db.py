#/usr/bin/env python3

from arango import ArangoClient
from datetime import tzinfo

# Configure your ArangoDB server connection here
conn = ArangoClient(protocol='http', host='192.168.42.152', port=8529, username='root', password='Qf5sc1ZOltQ7z4ab')

dbName = 'polBotCheck'
if dbName not in conn.databases():
    db = conn.create_database(dbName)
db = conn.db(dbName)

def getCollection(collectionName, edge=False):
    collectionNames = map(lambda c: c['name'], db.collections())
    if collectionName not in collectionNames:
        db.create_collection(collectionName, edge=edge)
    return db.collection(collectionName)

def getGraph(graphName):
    graphNames = map(lambda g: g['name'], db.graphs())
    if graphName not in graphNames:
        db.create_graph(graphName)
    return db.graph(graphName)

def getEdgeDefinition(graph, edgeDefName, fromCollections, toCollections):
    definitionNames = map(lambda d: d['name'], graph.edge_definitions())
    if edgeDefName not in definitionNames:
        graph.create_edge_definition(
            name=edgeDefName,
            from_collections=fromCollections,
            to_collections=toCollections
        )
    return graph.edge_collection(edgeDefName)

# create the collections we need, if necessary
usersCol = getCollection('users')
followersGraph = getGraph('followers')
followersCol = getEdgeDefinition(followersGraph, 'followers', ['users'], ['users'])

def saveUser(user):
    if not usersCol.has(user):
        usersCol.insert({'_key': user})

def getUserEdgeDoc(fromName='', toName=''):
    return {'_from': 'users/'+ fromName, '_to': 'users/' + toName}

def hasFollower(fromName='', toName=''):
    return followersCol.find(getUserEdgeDoc(fromName=fromName, toName=toName), None, 1).count() >= 0

def saveFollower(username, follower, botness):
    doc = {'_key': follower.screen_name, 'botness': botness}
    doc['followerOf'+username] = follower._json
    if usersCol.has(doc['_key']):
        usersCol.update(doc)
    else:
        usersCol.insert(doc)
    
    if not hasFollower(fromName=follower.screen_name, toName=username):
        followersCol.insert(getUserEdgeDoc(fromName=follower.screen_name, toName=username))

def saveTweet(tweet, retweets):
    raise NotImplementedError

def saveWordFreqs(wordFreqs):
    raise NotImplementedError
