"""
==============================
interface plugin documentation
==============================

"""

class IPluginInterface(object):
    """
    group of interfaces
    """

    interfaces = [] # List of interface names

    def __call__(self):
        """
        return a list of interface classes
        """
