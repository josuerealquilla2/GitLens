import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GitLents.settings')

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
