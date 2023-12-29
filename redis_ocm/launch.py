#https://isotoma.com/blog/2009/09/08/debugging-django-unit-tests-with-wing-ide/
"""
set manage.py as main debug file and then provide cmd as argument
set bp anywhere in src
"""
#in django shell
import os,sys
def start_django(project):
   dest=f"../{project}/"
   try: 
     os.chdir(dest)
   except:
       print(f"unable to change to {dest}")
   sys.path[0]=os.getcwd()
   setstr="{project}{sep}settings"
   set_path=setstr.format(project=project,sep="/")+".py"
   set_module=setstr.format(project=project,sep=".")
   if not os.path.exists(set_path):
     print(f"cant find settings file {set_path}")
     return
   os.environ.setdefault('DJANGO_SETTINGS_MODULE',set_module)
   import django
   django.setup()

from django.core.management import call_command
def mgmnt_cmd(cmd_param_list):
  call_command(cmd_param_list)

start_django("hacker_dal")
mgmnt_cmd("runserver")