from django.test import TestCase

# Create your tests here.
from django.test import SimpleTestCase,TestCase,override_settings
class Test_r_fns(TestCase):
    def setupClass(cls):
        pass

"""
NOTE:TestCase derived classes failed in setup due to problems in copying databases. This seems related to
using database routers
so for now have skipped TestCase classes and am using unittest
"""
from redis_ocm.hook_compilers import *
class Test_hook(TestCase):
    databases={'default','redis_db'}
    def test_hook_installed(self):
        HookCompilers().hook_compilers()
    def test_repeat_sub(self):
        pass

from redis_ocm.models import *
from redis_ocm.redis_compiler import get_redis_connection
import subprocess
class Helper():
    """ Sets up env independently. Can be used in TestCase, UnitTest or stand alone
    """
    update=lambda **kwArgs: ET1.objects.using("redis_db").update(**kwArgs)
    filter=lambda **kwArgs: ET1.objects.enable_cache().using("redis_db").filter(**kwArgs)
    @classmethod
    def ensureOneOrMoreRows(cls):
        et=ET1.objects.filter(id=1)
        if  len(et)==0: 
            ET1.objects.create(name="Hello",age=20)

    @classmethod
    def setup(cls):
        HookCompilers().hook_compilers()
        #https://stackoverflow.com/questions/89228/how-do-i-execute-a-program-or-call-a-system-command
        """the script does not return even though it starts background.
           so just start_redis through cmdline for now before running tests
            update:turned out it seems the output causes the non-return so now 
            output is redirected
        """
        subprocess.run("start_redis.sh>/tmp/redis.out;sleep 10",shell=True)
    @classmethod
    def cache_miss(cls,qs_reqd=False):
        cls.del_rkey("redis_ocm_et1:1")
        qs=cls.filter(id=1)
        if qs_reqd:
          return qs[0],qs
        return qs[0]

    @classmethod
    def cache_hit(cls,qs_reqd=False):
        cls.filter(id=1)[0]
        qs=cls.filter(id=1)
        if qs_reqd:
          return qs[0],qs
        return qs[0]

    @classmethod
    def get_redis_objects(cls):
       cls.ensureOneOrMoreRows()
       et=cls.filter(id=1)      
       r_objects=[row.redis for row in et]
       return r_objects
    @classmethod
    def update_incr(cls,**kwargs):
       cls.update(id=1,age=20)
       obj=cls.cache_miss()
       kparam={}
       for field in kwargs.keys():
         val=kwargs[field]
         kparam[field]=R(field)+val
       obj.redis.update(**kparam)
       return cls.read_rkey(obj.redis.rkey)
    
    @classmethod
    def del_rkey(cls,rkey):
       get_redis_connection().delete(rkey)
    @classmethod
    def create_or_update_rkey(cls,rkey, hkey_dict):
       get_redis_connection().hset(rkey,hkey_dict)
    @classmethod
    def read_rkey(cls,rkey, hkey_list=None):
       if not hkey_list: return get_redis_connection().hgetall(rkey)
       return get_redis_connection().hmget(rkey,hkey_list)
       

#@override_settings(DATABASE_ROUTER=[],DEFAULT_DB_ALIAS="redis_db")
class Test_hooked_model(TestCase):
    databases={'redis_db'}
    def setupTestData():
        super().setupTestData()
        Helper.setup()
    def test_cache_miss_select(self):
        Helper.cache_miss()

# Create your tests here.
import unittest
class Test_py_hooked_model(unittest.TestCase):
    #databases={'redis_db'}
    @classmethod    
    def setUpClass(cls):
        super().setUpClass()
        Helper.setup()
    def test_cache_miss(self):
        Helper.cache_miss()
    def test_cache_hit(self):
        Helper.cache_hit()
    def test_redis_property(self):
        obj=Helper.cache_hit()
        print("cache hit",obj.redis)
        obj=Helper.cache_miss()
        print("cache miss",obj.redis)

    def test_update_incr(self):
       val=Helper.update_incr(age=4)
       print(val)

from redis_ocm.redis_expressions import RHashKey ,R
class Test_r_expressions_rkey_does_not_exist(unittest.TestCase):
  
  @classmethod
  def setUpClass(cls):
     super().setUpClass()
     Helper.setup()
     Helper.del_rkey("trkey")
  def test_r_incr(self):
    val=RHashKey("trkey").update(tfield=R("tfield")+4)

class Test_r_expressions_rkey_exists(unittest.TestCase):
  
  @classmethod
  def setUpClass(cls):
     super().setUpClass()
     Helper.setup()
     Helper.create_or_update_rkey("trkey","tfield",0)
  def test_r_incr(self):
    val=RHashKey("trkey").update(tfield=R("tfield")+4)

class Test_rkey_create(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
     super().setUpClass()
     Helper.setup()
  
  def test_rkey_created(self):
         Helper.get_redis_objects()

