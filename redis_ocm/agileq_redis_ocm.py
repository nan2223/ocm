#https://www.agiliq.com/blog/2019/11/writing-an-orm-for-redis/#another-model-subclass
connection = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
'''
Since redis lacks auto-increment we have a key that stores latest id.
Model instances get their ids by incrementing that key
'''
class Question(Model):
 def __init__(self, id=None, question_text=None):
        if id is not None:
            id = int(id)
        self.id = id
        self.question_text = question_text

@classmethod
def latest_instance_id_key(cls):
#key that stores lastest instance
    class_name = cls.__name__.lower() # Convert class `Question` to string `question`
    return '%s-latest-id' % (class_name,)

def add_to_list(self):
#adds instance id to the list of instance ids 
    list_key = self.list_key()
    connection.lpush(list_key, self.id)

@classmethod
def list_key(cls):
#key name of list that stores instance ids
    class_name = cls.__name__.lower()
    return '%ss' % (class_name,) # Convert class `Question` to `questions`

@classmethod
def latest_instance_id(cls):
    return int(connection.get(cls.latest_instance_id_key()))

def increment_latest_instance_id(self):
    connection.incr(self.latest_instance_id_key())

@classmethod
def get_question(cls, id):
   def get(id):
      key = cls.cache_key(id)
      d = connection.hgetall(key)
      #return Question(**d)
      return cls.__name__(**d)

@classmethod
def cache_key(cls, identifier=None):
#key for object instance
    if identifier is None:
        identifier = cls.latest_instance_id() + 1
    class_name = cls.__name__.lower()
    return '%s-%d' % (class_name, int(identifier))

@classmethod
def get_questions(cls):
    list_key = cls.list_key()'query'
    instances = []
    for question_id in connection.lrange(list_key, 0, -1):
        question = cls.get_question(quest'query'ion_id)
        instances.append(question)
    return instances'query'

def save(self):
    key = self.cache_key()
    self.id = self.latest_instance_id() + 1
    connection.hmset(key, self.repr())
    self.increment_latest_instance_id()
    self.add_to_list()
    return self