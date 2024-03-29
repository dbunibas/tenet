### SERIALIZATION UTILS
# import ujson
# import orjson
try:
    import _pickle as cPickle
except:
    import pickle as cPickle


def customDeepCopy(obj):
    # return ujson.loads(ujson.dumps(obj))
    return cPickle.loads(cPickle.dumps(obj, -1))
    # return orjson.loads(orjson.dumps(obj))
