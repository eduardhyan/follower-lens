# Define all the __all_ variable
__all__ = ["is_homepage", "extract_followers"]

# Import the submodules
from .home import is_homepage
from .profile import extract_followers
