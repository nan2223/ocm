from redis_ocm.utils import *
compiler_module_cache=None
old_compiler_fn_ref={} #old ops.compiler fn
compiler_obj_map={} #{new_compiler_obj:old_compiler_obj
def enable_cache(self):
   """this fn is attached to model Manager class and hence not made part of HookCompilers
   """
   #assumes model Manager object is passed
   qs=self.get_queryset()
   if qs.query:
      qs.query.cache=True
   else:
      print("Error qs has no query")
   return qs
class HookCompilers():
   
   def ops_compiler_wrapper(self,old_f,obj,using):
     global old_compiler_fn_ref
     old_compiler_fn_ref[using]=old_f
     import importlib
     def do_ops_compiler( compiler_name):
               
         #                                                                      
         global compiler_module_cache
         print("compiler name is %s  " % (compiler_name))                                                                       
         #cut-paste from base.operations.compiler                               
         #compiler_module="django_any_backend.backends.dj_compiler"              
         compiler_module=REDIS_QUERY_COMPILER_MODULE
         if compiler_module_cache is None:                                      
            compiler_module_cache=importlib.import_module(compiler_module)      
         compiler_ref=getattr(compiler_module_cache,compiler_name)              
         return compiler_ref
                          
     return do_ops_compiler
   def substitute_method(self, obj,method_name,wrapper,using):
         old_method=getattr(obj,method_name,None)
         if old_method != None:
            new_method = wrapper(old_method,obj,using)
            #Dont substitute if we have already done it
            if type(old_method) != type(new_method):
              setattr(obj,method_name,new_method)
   
   def hook_compilers(self):
      from django.db import connections
      from django.db.models.query import QuerySet
      for c in connections:
         obj=connections[c].ops
         self.substitute_method(obj,'compiler',self.ops_compiler_wrapper,c)
      #add cache method to qs
      for m in HookCompilers.get_models(app_name="redis_ocm"):
        #need to handle custom manager names right now assume objects
        #for instance fn needs to be bound see So below
        setattr(m.objects,"enable_cache",enable_cache.__get__(m.objects))
        #https://stackoverflow.com/questions/972/addhttps://stackoverflow.com/questions/972/adding-a-method-to-an-existing-object-instanceing-a-method-to-an-existing-object-instance
   @classmethod
   def get_compiler_fn_ref(cls,using):
      """return the old ops.compiler fn"""
      try:
        return old_compiler_fn_ref[using]
      except Exception as e:
         print(f"exception {e}" )
         return None
   @classmethod
   def is_cached(cls,query):
      return  getattr(query,"cache",None)
   @classmethod
   def get_old_compiler_obj(cls,compiler_obj):
      cfn= old_compiler_fn_ref.get(compiler_obj.using,None)
      if not cfn:
         print(f"{compiler_obj.using} not valid")
         return None #tbd-throw?
      cref=cfn(compiler_obj.query.compiler) #tbd compiler params
      new_c=compiler_obj_map.get(compiler_obj,None)
      if not new_c:
        #create compiler obj
        new_c= cref(compiler_obj.query,compiler_obj.connection,compiler_obj.using)
        if len(compiler_obj_map)>1:
           print("Oops! compiler-obj_map > 1")
        #update map
        compiler_obj_map.clear()
        compiler_obj_map[compiler_obj]=new_c
      return new_c
   @classmethod
   def do_execute_sql(cls,compiler_obj,*args,**kwargs):
       #query. not None
       return cls.get_old_compiler_obj(compiler_obj).execute_sql(*args,**kwargs)
   @classmethod
   def do_results_iter(cls, compiler_obj,**kwargs):
      return cls.get_old_compiler_obj(compiler_obj).results_iter(**kwargs)
   @classmethod
   def get_models(cls, app_name='all'):
     #https://stackoverflow.com/questions/4111244/get-a-list-of-all-installed-applications-in-django-and-their-attributes
     #https://stackoverflow.com/questions/1125107/django-how-can-i-find-a-list-of-models-that-the-orm-knows
     from django.apps import apps
     models=[]
     def get_app_models(app_name):
       l=apps.app_configs.get(app_name,None)
       return l.get_models() if l else None
     if app_name != "all":
        models.extend(get_app_models(app_name))
     else:
        for an in apps.app_configs.keys():
            models.extend (get_app_models(an))
     return models
           
class HookGetCompiler():
   """NOT IN USE"""
   old_f=None
   @classmethod
   def new_get_compiler(cls,using=None, connection=None):
                
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
        
              return compiler_ref(obj,conn,using)
           
           return old_f(using, connection)
        
   @classmethod      
   def substitute_method(cls,method_name,new_method):
      old_method=getattr(cls,method_name,None)
      if old_method != None:
         setattr(cls,method_name,new_method)   
      else:
         print(f"no such method {old_method}")
         
   @classmethod
   def do_execute_sql(cls,query,*args,**kwargs):
       #query. not None
       return cls.old_f(query,query.connection,query.using).execute_sql(*args,**kwargs)
       
