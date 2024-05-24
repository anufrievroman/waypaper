"""Module to store acces application metadata"""
from importlib_metadata import metadata

class AboutData():
    """This class stores application about data in a central place"""
    def __init__(self):
        """Create AboutData object."""
        self.__app_metadata = metadata(__package__)
    def applicationName(self) -> str:
        """Get application name."""
        return self.__app_metadata['Name']
    def applicationSummary(self) -> str:
        """Get the summary of the application."""
        return self.__app_metadata['Summary']
    def applicationLogo(self) -> str:
        """Get the path to the application logo."""
        return str(self.__app_metadata['Name']) + ".svg"
    def applicationVersion(self) -> str:
        """Get application version."""
        return self.__app_metadata['Version']
    def homePage(self) -> str:
        """Get the URL of the application home page."""
        return self.__app_metadata['Home-page']
    def Author(self) -> str:
        """Get the name of the author of the application."""
        return self.__app_metadata['Author']
