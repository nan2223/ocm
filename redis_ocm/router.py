#https://docs.djangoproject.com/en/3.1/topics/db/multi-db/#automatic-database-routing

class RedisRouter:
    """
    A router to control all database operations on models in the
    auth and contenttypes applications.
    """
    route_app_labels = {'redis_ocm' }
    def route_model(self,model):
        if model._meta.app_label in self.route_app_labels:
           #changed default alias to redis_db. Now only those that requie other db
           #need to be put in the dict
           alias={'picklemodel':'pickle_db','redistest':'redis_db','redismodel':'redis_db',\
           'rd':'redis_db','rD':'redis_db','fk':'redis_db','fkp':'redis_db','m2m':'redis_db'\
           ,'fkgp':'redis_db'}.get(model._meta.model_name,'redis_db')
           #alias='pickle_db' if hasattr(model, 'non_db') else 'redis_db'
           return alias
        return 'default' #None =not sure if None will result in defalut?

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        return self.route_model(model)

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        return self.route_model(model)

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        a1=self.route_model(obj1);a2=self.route_model(obj2)
        if a1 != a2:
            print(f"router got relation in diff dbs:{obj1}:{a1},{obj2}:{a2}")
            #import pdb;pdb.set_trace()
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """
        if app_label in self.route_app_labels:
            return db == 'redis_db'
        return None
