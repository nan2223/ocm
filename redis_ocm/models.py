from django.db import models
from redis_ocm import redis_ocm
# Create your models here.
class RedisTest(models.Model):
    class Meta:
      base_manager_name='objects'
    name = models.CharField(max_length=100)
    age = models.IntegerField()
#Update: Adding lastAccessed for extar work in builtin cbv
#allowing null will let existing rows stay as is
    last_accessed = models.DateTimeField(null=True)
#    objects=models.Manager.from_queryset(redis_ocm.RedisQuerySet)()
    objects=redis_ocm.RedisManager.from_queryset(redis_ocm.RedisQuerySet)()  
    #adding default manager so that its used in save?
    default_manager=objects

class RedisModel(RedisTest):
    pass

class PickleModel(RedisTest):
    non_db='pickle_db'
    max_per_request = 100

class RD(models.Model):
    #class Meta:
    #  base_manager_name='objects'
    name = models.CharField(max_length=100)
    age = models.IntegerField()
#Update: Adding lastAccessed for extar work in builtin cbv
#allowing null will let existing rows stay as is
    last_accessed = models.DateTimeField(null=True)
#    objects=models.Manager.from_queryset(redis_ocm.RedisQuerySet)()
    objects=redis_ocm.RedisManager.from_queryset(redis_ocm.RedisQuerySet)()  
    #adding default manager so that its used in save?
    default_manager=objects

class FK(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()

class M2M(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()

class FKP(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    m2m = models.ManyToManyField(M2M)
    fk = models.ForeignKey(FK, on_delete=models.CASCADE)

#migration 007-added the GP class
class FKGP(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    m2m = models.ManyToManyField(FKP)


#mig..ration -0005 .embed a class. ET is completely ignored in migration
class ET:
    name = models.CharField(max_length=100)
    age = models.IntegerField()

class PT(models.Model):
   et=ET()

#migration 006.embed another model. Embedded model is not linked in any way
#two independent models are created
class ET1(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()

class PT1(models.Model):
   et=ET()

""" Web shopping cart
"""
class DummyUser(models.Model):
    name=models.CharField(max_length=100)

class Login(models.Model):
    user=models.ForeignKey(DummyUser,on_delete=models.CASCADE)
    name=models.CharField(max_length=250)
    time=models.DateTimeField()
    token=models.CharField(max_length=100)

class Product(models.Model):
    name=models.CharField(max_length=100)
    price=models.IntegerField()

class Viewed(models.Model):
    token=models.ForeignKey(Login,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    time=models.DateTimeField()