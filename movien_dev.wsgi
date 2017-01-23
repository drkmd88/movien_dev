import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.append('/var/www/movien_dev')
from app import app as application
