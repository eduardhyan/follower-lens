import os
import re
import sys

import inquirer
from inquirer.themes import BlueComposure
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import commands


import config

console = Console()


def print_introduction():
    """
    Prints an introduction message to the user.
    """
    title = Text("📸 Follower Lens 📸", style="bold cyan underline")

    welcome_message = """
    👋 Welcome to Follower Lens!  

    Ever wondered who truly follows you back on Instagram?  
    Let's uncover the reality—who's loyal, who's ghosting, and who’s just not that into you.  

    🔍 First let's find your account on Instagram!
    """

    console.print(Panel.fit(welcome_message, title=title, style="bold green"))


def ask_for_username():
    """Keep asking until a valid username is provided."""
    while True:
        questions = [inquirer.Text("username", message="Enter your username")]
        answers = inquirer.prompt(questions, theme=BlueComposure())
        username = answers["username"].strip() if answers["username"] else ""

        if username:
            return username
        else:
            print("⚠️ Username cannot be empty. Please try again.")


def ask_for_email():
    """Keep asking until a valid email is provided."""
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    while True:
        questions = [inquirer.Text("email", message="Enter your email")]
        answers = inquirer.prompt(questions, theme=BlueComposure())
        email = answers["email"].strip() if answers["email"] else ""

        if re.match(email_pattern, email):
            return email
        else:
            print("⚠️ Invalid email format. Please enter a valid email address.")


def ask_for_password():
    """Keep asking until a valid password is provided."""
    while True:
        questions = [inquirer.Password("password", message="Enter your password")]
        answers = inquirer.prompt(questions, theme=BlueComposure())
        password = answers["password"].strip() if answers["password"] else ""

        if len(password) >= 6:
            return password
        else:
            print("⚠️ Password must be at least 6 characters long. Please try again.")


def prompt_for_credentials():
    """
    Prompts the user to enter their credentials.

    Returns:
        tuple: A tuple containing the username, email, and password.
    """
    print("Please provide your account details:")

    answers = {}
    answers["username"] = ask_for_username()

    is_public = commands.profile.check_if_account_is_public(answers["username"])

    if not is_public:
        message = (
            "[bold red]This account is private![/bold red]\n\n"
            "🔒 To continue, please make your account [bold]public[/bold] and rerun the program.\n"
            "Alternatively, you can provide your credentials ([bold]email[/bold] and [bold]password[/bold]) "
            "to allow us to access your \nfollower data and identify who doesn’t follow you back."
        )

        console.print(
            Panel.fit(message, title="[cyan]Access Restricted[/cyan]", style="red")
        )

        # Ask user for their preferred method
        questions = [
            inquirer.List(
                "method",
                message="Which method would you like to use?",
                choices=[
                    (
                        "🔓 I'll change my account type to public and rerun the app.",
                        "manual",
                    ),
                    ("✉️ I want to enter my email and password.", "auto"),
                ],
            )
        ]

        method_answers = inquirer.prompt(questions, theme=BlueComposure())

        if method_answers["method"] == "manual":
            console.print("\n[bold green]Got it![/bold green] ✅")
            console.print(
                "Please change your Instagram account to [bold cyan]public[/bold cyan] and restart the app."
            )
            console.print(
                "Once your account is public, you'll be able to proceed without providing credentials.\n"
            )
            sys.exit(0)
        else:
            answers["email"] = ask_for_email()
            answers["password"] = ask_for_password()

    print("\n✅ Account details received!")
    print(f"Username: {answers['username']}")
    print(f"Private: {not is_public}")

    if not is_public:
        print(f"Email: {answers['email']}")
        print("Password: 🔒 (Hidden for security)\n")

    return (
        answers.get("username"),
        answers.get("email", None),
        answers.get("password", None),
        is_public,
    )


def get_credentials():
    """
    Retrieves user credentials. If stored credentials are found, prompts the user to reuse them.
    Otherwise, prompts the user to enter new credentials and saves them.
    """
    if config.Account.init_credentials():
        questions = [
            inquirer.List(
                "proceed",
                message=f"Are you '{config.Account.username}'?",
                choices=["yes", "no"],
                default="yes",
            ),
        ]

        answers = inquirer.prompt(questions, theme=BlueComposure())

        # We have credentials, no need to ask for them again
        if answers["proceed"] == "yes":
            return

    username, email, password, is_public = prompt_for_credentials()
    config.Account.save_credentials(
        username=username, email=email, password=password, is_public=is_public
    )


def clear():
    # for windows
    if os.name == "nt":
        _ = os.system("cls")
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system("clear")
