# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, '/var/www/u0591011/data/www/u0591011.isp.regruhosting.ru/parsys')
sys.path.insert(1, '/var/www/u0591011/data/djangoenv/lib/python3.7/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'parsys.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()