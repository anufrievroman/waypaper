"""Module to store acces application metadata"""
from importlib_metadata import metadata

class AboutData():
    """This class stores application about data in a central place"""
    def __init__(self):
        self.__app_metadata = metadata(__package__)
    def applicationName(self):
        return self.__app_metadata['Name']
    def applicationSummary(self):
        return self.__app_metadata['Summary']
    def applicationLogo(self):
        return str(self.__app_metadata['Name'])+".svg"
    def applicationVersion(self):
        return self.__app_metadata['Version'] # pylint: disable=no-member
    def homePage(self):
        return self.__app_metadata['Home-page']
    def Author(self):
        return self.__app_metadata['Author']
