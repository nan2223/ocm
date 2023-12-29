from django.db.models.expressions import *
from redis_ocm.redis_compiler import r_incr,r_decr

""" *********
combine derivation -not required for now
***************
class RCombinable():
   #Use this class to hide Combinable's _combine by placing this ahead in multiple inheritance . 
   def _combine(self, other, connector, reversed):                                                    
        if not hasattr(other, 'resolve_expression'):                                                   
            # everything must be resolvable to an expression                                           
            if isinstance(other, datetime.timedelta):                                                  
                other = DurationValue(other, output_field=fields.DurationField())                      
            else:                                                                                      
                other = ValuUpdating db field aggregates not yet implementede(other)                                                                   
                                                                                                       
        if reversed:                                                                                   
            return RCombinedExpression(other, connector, self)                                          
        return RCombinedExpression(self, connector, other)

class RCombinedExpression(CombinedExpression):

class R(RCombinable,F):
"""#end  comment

class R():
  def __init__(self,field):
    self.field=field
  def __add__(self,num):
    return RCE(self,"+",num)

class RCE():
  def __init__(self,lhs,op,rhs):
    self.lhs=lhs ; self.op=op ; self.rhs=rhs
  def combine(self,rkey=None,hkey=None):
    add=lambda : r_incr(rkey=rkey,hkey=hkey,value=self.rhs)
    sub=lambda : r_incr(rkey=rkey,hkey=hkey,value=-self.rhs)
    do_fn={"+":add,"-":sub}.get(self.op,None)
    if not do_fn:
      print("Ooops no op in R expression")
    else:
      do_fn()

TYPE_RCE=type(RCE(None,None,None))

class Db_Row():
   pass

TYPE_DB_ROW=type(Db_Row())

class RKey():
  """Represents a redis key. 
     type should be SCALAR for single value and AGGREGATE for multi value fields like hash,set
      rkey_db_field is the field it represents in db. for aggregate types if this key represents a row then this should
      be TYPE_DB_ROW, else its the name of the field which has json encoded name=value list
     query_id is the query that created this key. may need this to do db update
     for aggregates multiple fields update can be supported in future
  """
  def __init__(self,rkey,rkey_db_field=TYPE_DB_ROW,query_id=None):
     """ a redis key can represent a db field or an entire row. 
         See above for info on params
     """
     self.rkey=rkey; self.rkey_db_field=rkey_db_field;self.query_id=query_id
  def _update(self,key_type="SCALAR",**kwargs):
      """For now assume this will be of form update(field=R expression)
       if field is pk, then db will throw exception
      """
      #Assumes atleast 1 kwarg
      rce=None;hkey=None;ret=[]
      num_args=len(kwargs)
      if self.rkey_db_field != TYPE_DB_ROW:
         print("Updating db field aggregates not yet implemented")
         return None
      for kwarg,rce in kwargs.items():
        if type(rce) != TYPE_RCE:
          print(f"{rce} is not of type RCE")
          return None
        if key_type == "SCALAR":
           if num_kwargs>1:
              print("No hkey should be provided for scalar")
              return None
           if self.rkey_db_field != rce.lhs:
              print(f"Expressions using other fields not supported. {field} != {rce.lhs}")
              return None
        """NOT REQD
         if type == "AGGREGATE":
            if not hkey:
                print("hkey required for aggregate")
               return None
            # check for pk alteration. for now let db handle it
            if not self.rkey_db_field and hkey and self.pk = hkey:
              print("{self.hkey} is pk and cannot be altered")
             return None
        """
        ret.append(rce.combine(rkey=self.rkey,hkey=kwarg))
      return ret

class  RHashKey(RKey):
  def __init__(self,rkey):
    super().__init__(rkey)

  def update(self,**kwargs):
    return super()._update(key_type="AGGREGATE",**kwargs)


