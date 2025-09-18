try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources

resources_dir = resources.files(__name__)
