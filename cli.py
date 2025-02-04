import getpass
import config


def print_introduction():
    """
    Prints an introduction message to the user.
    """
    print("=" * 40)
    print("Welcome to Follower Lens")
    print("Please enter your credentials to continue")
    print("=" * 40)


def prompt_for_credentials():
    """
    Prompts the user to enter their credentials.

    Returns:
        tuple: A tuple containing the username, email, and password.
    """
    print("\nPlease provide your credentials:")
    username = input("Username: ")
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    return username, email, password


def get_credentials():
    """
    Retrieves user credentials. If stored credentials are found, prompts the user to reuse them.
    Otherwise, prompts the user to enter new credentials and saves them.
    """
    print_introduction()
    if config.Account.init_credentials():
        reuse = (
            input(
                f"Stored credentials for '{config.Account.username}' found. Would you like to reuse them? (Y/n): "
            )
            .strip()
            .lower()
        )
        if reuse != "n":
            return

    username, email, password = prompt_for_credentials()
    config.Account.save_credentials(username=username, email=email, password=password)
