class BaseConfig(object):
    '''
    Base config class
    '''
    DEBUG = True
    TESTING = False


class ProductionConfig(object):
    """
    Production specific config
    """
    DEBUG = False


class DevelopmentConfig(object):
    """
    Development environment specific configuration
    """
    DEBUG = True
    TESTING = True
