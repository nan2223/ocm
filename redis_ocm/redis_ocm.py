#custom mgr,queryset
#will try to add custom query to our qs
from django.db import models
import importlib
from django.db import connections


  #For chained objects get_compiler points to new_get_compiler
  #for objects that have not been chained get_compiler resolves to our
  #implementation below
  #both those methods delegate to this method which actually does the work
compiler_module_cache=None
def do_get_compiler( using=None, connection=None,compiler_name=None,old_f=None):
       #self.old_f=super().get_compiler if (not self.old_f) or self.old_f == self.get_compiler else self.old_f
       #old_f=super().get_compiler if (not old_f)  else old_f
       print("compiler name is %s using=%s connection=%s " % (compiler_name,using,connection))
       #
       #new fnality-if conn is not pickle_db will use dab*compiler
       #overriding the configured compiler in backend
       #else will let compile configured in backend be used 
       #this code is based on dj*sql*compiler which is cut-paste later for ref  
       if using and using == "redis_db": 
         #
         global compiler_module_cache

         #cut-paste from base.operations.compiler
         compiler_module="django_any_backend.backends.dj_compiler"
         if compiler_module_cache is None:
            compiler_module_cache=importlib.import_module(compiler_module)
         compiler_ref=getattr(compiler_module_cache,compiler_name)
         
         #when var name is connection it seems to be set to nothing will 
         #rename it to conn and now it works! why???
         conn=connections[using]
         
         return (compiler_ref,conn)
         #compiler=compiler_ref(self, conn, using)
         #self.compilers.append(compiler)
         #return compiler
       #1.old_f(**kwargs) produces using multiple defn error
       #after debugging using a snipppet what is happening is old_f was sent in it
       # and so self should not be passed. 
       #with self it turns out to be self,using=self,kwargs={"using"="db"}
       #dy has self embedded!                                                   
       #so just use **kwargs old_f already has self embedded!      
       return old_f(using, connection) if old_f else None # old_f(**kwargs)

class RedisQuery(models.sql.Query):
  #we can override get_compiler and make it return our custom compiler

  #below causes error since i think super not yet constructed? 
  #old_f=super().get_c'ompiler
  old_f=None
  #
  compiler_module_cache=None
  compilers=[]
  
  #for get, chain is not called and so we override get_compiler. 
  #for other queries we will substitute in chain?
  #
  #db/models/query.py", line 752, in update
  #    rows = query.get_compiler(self.db).execute_sql(CURSOR)   
  #TypeError: get_compiler() takes 0 positional arguments but 1 was given
  #explanation:
  #using **kwargs to gather caused problem since passing a single positional param
  # wontget_query get mapped to 1st kwarg! many places in query use thus form and so it
  # failed . expanding args to key=value list solved this!
  #
  def get_compiler(self, using=None, connection=None):
     #delegate to inner
     compiler_ref,conn=do_get_compiler(using,connection,self.compiler)
     return compiler_ref(self,conn.using)

  #
  #wrapper holds self and old_f for nested method

  def get_compiler_wrapper(self,old_f,obj):

  #get_compiler only has kw args so skip args. also self wont be passed
  #to this nested method so we pick object up from wrapper param

  #
  #instead of storing old_f in self:   self.old_f=old_f
  # we will not store it in self and pass it as param thereby avoiding 
  #do_get_compiler being dependent on self for old_f
  #
    #
    #renamed get_compiler to new_get_compiler to avoid clash with 
    # the top level override
    def new_get_compiler(using=None, connection=None):
       #self will go to older object we need to use chained object
       #becuase it will have the updated query
       #self.get_compiler(using, connection) 
       #return obj.do_get_compiler(using, connection)  #old_f(**kwargs)
       #             ^

       #if we chain a chained object old_f will be this method and 
       #passing that  to do will cause do to call this method back setting
       #up infinite recursion.
       #so if this method is already old_f pass old_f=None so that super() is called 
       #
       #trying to check value of old_f lead to error:
       #UnboundLocalError: local variable 'old_f' referenced before assignment
       #so adding nonlocal to make it refer to outer scope var       
       nonlocal old_f,obj
       if old_f == self.get_compiler:
          old_f = None
       compiler_ref,conn=do_get_compiler(using, connection,obj.compiler,old_f)
       return compiler_ref(obj,conn,using)
    return new_get_compiler
  def substitute_method(self, obj,method_name,wrapper):
    old_method=getattr(obj,method_name,None)
    if old_method != None:
       new_method = wrapper(self,old_method,obj)
       setattr(obj,method_name,new_method)
  def chain(self, klass=None):
      print("chain")
      method_name="get_compiler"
      ret = super().chain(klass)
      print("from %s chained=%s " % (ret.__repr__(),self.__repr__()))
      self.substitute_method(ret,method_name,RedisQuery.get_compiler_wrapper)
      return ret
  #ns cut-paste from sql.query
  def dj_get_compiler(self, using=None, connection=None):
      if using is None and connection is None:
           raise ValueError("Need either using or connection")
      if using:
          connection = connections[using]
      return connection.ops.compiler(self.compiler)(self, connection, using)

class RedisIterable(models.query.ModelIterable):
    def __iter__(self):
      return super().__iter__()

class RedisQuerySet(models.query.QuerySet):
   #I initially has no arg, then added model since base needed it
   #def __init__(self,model):
   #turns out we need all args in clone so i have added them
   #
   #another buf in py -says invalid syntax when : is missed. it could say
   #missing :
   def __init__( self, model=None, query=None, using=None, hints=None):
      super().__init__(model,query,using,hints)
      #override modelIterable with our version
      self._iterable_class = RedisIterable
   #no need to overide _fetch_all since are overriding __iter__ of the Iterable
   #
   #TypeError: _fetch_all() takes 0 positional arguments but 1 was given
   #had forgotten to add self as param
   def _fetch_all(self):
      print("override _fetch_all")
      return super()._fetch_all()

#may not require custom manager since we can use from_Qs to get a mgr
#that yuses our qs
class RedisManager(models.Manager):
    def get_queryset(self):
        #doc says pass using but this causes unexpected arg error
        #TypeError: __init__() got an unexpected keyword argument 'using'
        #sae thing happens when default Manager is used
        #will omit using and see
        #return RedisQuerySet(self.model, using=self._db)
        #DUh I think this is because I had omiited init in QS init
        #
        #new error: NameError: name 'model' is not defined
        #Duh I had been thinking model is not set in base and was 
        #trying to see when its set
        #turns out stupid error -not using self while creating RedisQuery
        # i had used RedisQuery(model) instead of RedisQuery(self.model)!!
        #but the error  could definately be more helpful and point where
        #it saw the problem as well as hint about using self
        return RedisQuerySet(self.model,query=RedisQuery(self.model))

#we can have all our models inherit from below which sets a custom mgr tied
#to our custom qs. we only need the qs but to use it we need a mgr wh will
#return our qs in get_queryset - i think
#causes:
#File "/mnt/sda6/django/lib64/python3.7/site-packages/django/db/models/base.py", line 115, in __new__
#    "INSTALLED_APPS." % (module, name)
#RuntimeError: Model class builtins.RedisBaseModel doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS.
#-FIX LATER COMMENT NOW
#class RedisBaseModel(models.Model):
#   objects=models.Manager.from_queryset(RedisQuerySet)()
