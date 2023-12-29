try:
  import redis
except:
  print(sys.exc_info())
rconn=None
def get_redis_connection():
  global rconn
  if not rconn:
    rconn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

  if not rconn:
      print("Unable to connect to redis server.Please ensure it is started")
  return rconn
  

get_redis_connection()

#helper
def _get_row_id(clause_dict):
  where_sql=clause_dict['WHERE']['sql']
  P='(?P<col>[^ ]+) = %s'
  import re
  where_col=re.match(P,where_sql).groupdict()['col']
  found_id_col = where_col.find( '_ptr_id"') != -1 or where_col.find( '"id"') != -1
  if not found_id_col:
    return None
  id=clause_dict['WHERE']['params'][0]
  return id

def get_key(clause_dict,id=None):
  table_name=clause_dict['query'].model._meta.db_table
  if not id:
    id=_get_row_id(clause_dict)
  key='%s:%s'%(table_name,id)
  return key
def get_insert_key(clause_dict,id):
  """this method is obsolete and should be removed
  """
  return get_key(clause_dict,id=id)

'''
  Getting base table name:
  The query.alias_map has base table and possible join objects.
  We want to get the base table name for this quey. It can be got
  from query.model._meta.db_table or we can just iterate over
  keys for a BaseTable object and then get the table name from there.

  Geting id of instance
  in where sql we look for id as col name and lookup param for value  at same index
  i think this will always be 1st index
  the sql where is of form col= %s so better to see if we can get the col from the
  where node itself.
  [1]where node is inherited from dj*.utils.tree.Node I think it has a Op and two params
  [2]the node has a attr children which is of Op Type. here id= 1 is an exact op
     and so it is a Exact type object. 
  [3]Exact derives from builtinlookop. 
     the lookup class is in dn.models.lookups. It has a base lookup from which a builtinlookup dervies.
  [4]Exact has a as_sql which is called. It in turn calls a process_lhs and a process_rhs
     to get the sql parts
     ch=query_clauses[0]['WHERE_NODE'].children
     ch[0].lhs
     Col(redis_ocm_fkp, redis_ocm.FKP.name)
     why is this displayed liked this instead of <..type..> object at <address>?
     it says type id <class 'django.db.models.expressions.Col'>
     so is lhs a class ref?
  [5]Col is class 'django.db.models.expressions.Col
     it takes an alias and a target. It seems target is a model attrbiute
     corresponding to a db col
     here target is redis_ocm.FKP.name and is of type django.db.models.query_utils.DeferredAttribute
  [6]deferred_aTTrtibute have an attribute field
  [7]attribute field is of different db col types. Here it is CharField
    So it seems that thogh wespecify type in defining a model column at load the attr is a generuc Col
    type object which internally has a type that identifies the specific type.
  [8] field has many attrs one of which is column and specifies column name
    so what does field represent? I think the db column. It has the name of the column and type
    the confusionhee seems to be that there is Col class which I think represents the model col
    and then there is the field which has a column attr which is the name of the db col
  [5]Col 'as _sql concats alias and target.column to give the table.col part of sql
  [4]process_rhs
     ch[0].rhs
     'dfd'
    get_db_prep_lookup
    get_db_prep_value(db/models/fields/__init__.py
  [4]get_rhs_op
      connection.operators[lookup_name] will return "= %s" for exact operator
      this will return "= %s"
  
  Filter/fetch limitation assumed for now
  We are assuming this is always fetch by id for now
  so we can simlply check that "where" is of form "table.id = %s" for now
  and extract table as a regex group. we could simply generate the where since we know
  we are only going to retreive the model based on id.

  Forming the redis key
  we only need to take the where param which has the reqired id
  in forming the redis key
  The redis key will be of form model:id, actually it may be app_label_model:id
  
  Fetching the cols
  The select cols are in the select sql in form "table"."col"
  we just fetch the col values using hmget specfying key
  as table:id
  we can do a sanity check that cols returned from redis are the same
  as in select sql clause. Perhaps the values need to be placed in some output form
  for higher layer?
  Now Join for FK, DB does matchng of row ids and then applies where clause on
  selected rows to get desired row
  in heirarchy we assume only forward relation and that FK col has unique value
  in yathey i.e.FK is actualy pk or a unique FK in target
  the join then is just lookup TO table by FK val
  multi relation lookup
  in example, we have blog, Author. Entry conects Blog and Author
  so to get blog by Author Blog.objects.filter(entry__author__name=val)
  which is from related (entry) move to next relation (author)
  in case of our heirarchy it would be
  2ndlevel.objects.filter(1stlevel__root__id=val)
'''
def _r_incr_decr(rkey=None,hkey=None,value=None,op="incr"):
   if op=="incr":
      h_op=rconn.hincrby
      op=rconn.incrby
   else:
      print("{op} not implemented")
      return
   if hkey:
     h_op(rkey,hkey,value)
   else:
     op(rkey,value)

def r_incr(rkey=None,hkey=None,value=None):
    return _r_incr_decr(rkey=rkey,hkey=hkey,value=value,op="incr")

def r_decr(rkey=None,hkey=None,value=None):
    return _r_incr_decr(rkey=rkey,hkey=hkey,value=value,op="decr")

def r_select(clause_dict):

  #clause_dict=query_clauses[query_index]
  cols=clause_dict['SELECT']['sql']
  #Col names in sELECT have table prefix but no such thing in update
  #lets strip table prefix and only use col name as key
  import re
  P='[^.]+[.]"(?P<col>.+)"'
  """In select id is also a col but in redis we put id in key. so it will be duplicated
  but we will leave it in col list since it iq required for model update
   removed this filter to allow id in cols if col.find('."id"')== -1
  """
  cols=[re.match(P,col).groupdict()['col']  for col in cols ]
  key=get_key(clause_dict)
  if not key:
    return [None],[None]
  print(f"r_select key: {key}")
  row=rconn.hmget(key,cols)
  return  [key],[row]

def r_update(clause_dict):
  import re
  P='(?P<col>[^ ]+) = %s'
  cols=clause_dict['UPDATE']['sql']
  cols=[re.match(P,col).groupdict()['col'] for col in cols]
  values=clause_dict['UPDATE']['params']
  params={}
  for i in zip(cols,values):
    params[i[0]]=i[1]
  key=get_key(clause_dict)
  if not key:
    return None
  rconn.hmset(key,params)

'''
  inheritance means members of class cam belong to diff tables.
  when creating RedisModel the members actually come from base RedisTest
  so the insert sql is for base RedisTest table.  if there are members
  in diff clases of the inheritance heirarchy then separate insert need to be done
  for each class since they are diff tables
  insert query: insert sql clause contains cols and VALUE clause contains values
  {'name': 'InsertCompiler', 'INSERT': {'sql': ['"name"', '"age"'], 'params': []}, 'TABLE': {'sql': ['"redis_ocm_fk"'], 'params': []}, 'VALUE': {'sql': [['ppp', 30]], 'params': []}}
 
  '''
def r_insert_params(clause_dict,insert_id,col_value_iter):
  """col_value is a tuple of (col,val). it is turned into dict params[col]=val
     so that it can be used in hmset
  """
  params={}
  for i in col_value_iter:
    params[i[0]]=i[1]
  key=get_key(clause_dict,id=insert_id)
  try:
    ret=rconn.hmset(key,params)
  except Exception as e:
    print(e)
    ret=None
  return key,ret

def r_insert(clause_dict,insert_id):
  cols=clause_dict['INSERT']['sql']
  values=clause_dict['VALUE']['sql'][0]
  return r_insert_params(clause_dict,insert_id,zip(cols,values))

def gen():
  '''
  FK is implemented by joining on cols and filtering on some col value
  M2M is implemented by having a rel_table with each row having id of participating
  row from the particpatng tables: 
  so A has 4 rows (r1-r4) related to 3 rows of B (r10-12) we have 3 rows in
  rel table (A.r1,B.r10), (A.r1, b.r11),(A.r1,B.r12) and so on
  if we want to cache a object with m2m we need to add a rel_table to cache with
  the rowids to be able o traverse the relationship-
  '''
