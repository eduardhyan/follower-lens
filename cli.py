"""
This module provides CLI-related functions for the Follower Lens application.
It includes functions for printing an introduction, prompting for user credentials,
and clearing the console.
"""

import os
import re

import inquirer
from inquirer.themes import BlueComposure
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from model import Account

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
    """
    Prompts the user to enter a valid username.

    Returns:
        str: The entered username.
    """
    while True:
        questions = [inquirer.Text("username", message="Enter your username")]
        answers = inquirer.prompt(questions, theme=BlueComposure())
        username = answers["username"].strip() if answers["username"] else ""

        if username:
            return username
        else:
            console.print("⚠️ [red]Username cannot be empty. Please try again.[/red]")


def ask_for_email():
    """
    Prompts the user to enter a valid email address.

    Returns:
        str: The entered email address.
    """
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    while True:
        questions = [inquirer.Text("email", message="Enter your email")]
        answers = inquirer.prompt(questions, theme=BlueComposure())
        email = answers["email"].strip() if answers["email"] else ""

        if re.match(email_pattern, email):
            return email
        else:
            console.print(
                "⚠️ [red]Invalid email format. Please enter a valid email address.[/red]"
            )


def ask_for_password():
    """
    Prompts the user to enter a valid password.

    Returns:
        str: The entered password.
    """
    while True:
        questions = [inquirer.Password("password", message="Enter your password")]
        answers = inquirer.prompt(questions, theme=BlueComposure())
        password = answers["password"].strip() if answers["password"] else ""

        if len(password) >= 6:
            return password
        else:
            console.print(
                "⚠️ [red]Password must be at least 6 characters long. Please try again.[/red]"
            )


def prompt_for_credentials():
    """
    Prompts the user to enter their credentials.

    Returns:
        tuple: A tuple containing the username, email, and password.
    """
    console.print("Please provide your account details:")

    username = ask_for_username()
    email = ask_for_email()
    password = ask_for_password()

    console.print("\n✅ [green]Account details received![/green]")
    console.print(f"Username: {username}")
    console.print(f"Email: {email}")
    console.print("Password: 🔒 (Hidden for security)\n")

    return username, email, password


def get_credentials(account: Account):
    """
    Retrieves user credentials. If stored credentials are found, prompts the user to reuse them.
    Otherwise, prompts the user to enter new credentials and saves them.
    """
    if account.load_credentials():
        questions = [
            inquirer.List(
                "proceed",
                message=f"Are you '{account.username}'?",
                choices=["yes", "no"],
                default="yes",
            ),
        ]

        answers = inquirer.prompt(questions, theme=BlueComposure())

        if answers["proceed"] == "yes":
            return

    username, email, password = prompt_for_credentials()
    account.save_credentials(username=username, email=email, password=password)


def clear():
    """
    Clears the console.
    """
    if os.name == "nt":
        _ = os.system("cls")
    else:
        _ = os.system("clear")
