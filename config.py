import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dsfgdfgf45645hfgh435SDFG345'