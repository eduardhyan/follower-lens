# 📸 Follower Lens 📸

Follower Lens is a tool designed to help you analyze your Instagram followers and followings. It provides insights into who follows you back, who doesn't, and who you follow but don't follow back. This tool leverages the Playwright library to interact with Instagram and the Rich library to display results in a user-friendly manner.

## Features

- **Analyze Followers**: Get a detailed list of your followers and followings.
- **Identify Unfollowers**: Find out who doesn't follow you back.
- **Identify Ghost Followers**: Find out who follows you but you don't follow back.
- **Cache Management**: Store and manage follower data locally to speed up analysis.
- **User-Friendly CLI**: Interact with the tool through a command-line interface with prompts and clear instructions.

## Demo

![Demo](.github/images/demo.gif)

## Installation

1. **Clone the repository**:

   ```sh
   git clone https://github.com/eduardhyan/follower-lens.git
   cd follower-lens
   ```

2. **Create a virtual environment**:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies**:

   ```sh
   pip3 install -r ./requirements.txt --index-url=https://pypi.org/simple
   ```

4. **Install Playwright browsers**:
   ```sh
   playwright install
   ```

## Usage

1. **Run the main script**:

   ```sh
   python3 main.py
   ```

2. **Follow the prompts**:
   - Enter your Instagram username, email, and password when prompted. Your credentials are securely encrypted to ensure your data is safe.
   - Choose one of the actions from the menu:
     - **Find Unfollowers**: Start finding people who don't follow you back.
     - **Preview Unfollowers**: Preview only people who don’t follow you back.
     - **Preview Ghosts**: Preview only people who follow you but you don't follow them.
     - **View Full Follower List**: Preview the full list of followers/non-followers.
     - **Clear the cache**: Delete locally stored data from previous executions.
     - **Cancel & Exit**: Close the application and exit.

## How It Works

1. **Authentication**:

   - The tool uses Playwright to log in to your Instagram account.
   - Credentials are securely stored using encryption.

2. **Data Extraction**:

   - The tool navigates to your profile and extracts the list of followers and followings.
   - Data is cached locally to speed up subsequent analyses.

3. **Data Analysis**:
   - The tool analyzes the extracted data to identify unfollowers and ghost followers.
   - Results are displayed in a user-friendly table format using the Rich library.

## Modules

- **[main.py](http://_vscodecontentref_/0)**: The main entry point for the tool. Handles user commands and runs the appropriate functions.
- **[auth.py](http://_vscodecontentref_/1)**: Provides authentication-related functions, including managing cookies and performing manual login.
- **[cache.py](http://_vscodecontentref_/2)**: Manages a cache of followers and followings using JSON files.
- **[console.py](http://_vscodecontentref_/3)**: Provides functions for printing messages and tables to the console using the Rich library.
- **[constants.py](http://_vscodecontentref_/4)**: Defines constants used throughout the application.
- **[cli.py](http://_vscodecontentref_/5)**: Provides CLI-related functions, including printing an introduction, prompting for user credentials, and clearing the console.
- **[commands](http://_vscodecontentref_/6)**: Contains modules for interacting with Instagram pages and extracting follower data.
- **[analyzer.py](http://_vscodecontentref_/7)**: Provides the [FollowerInsights](http://_vscodecontentref_/8) class for analyzing follower and following data.
- **[model.py](http://_vscodecontentref_/9)**: Defines the [Account](http://_vscodecontentref_/10) class for managing user credentials.
- **[utils](http://_vscodecontentref_/11)**: Contains utility functions for managing session paths and encryption.

## Requirements

- Python 3.10+
- Playwright
- Rich
- Inquirer
- Cryptography

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Acknowledgements

- [Playwright](https://playwright.dev/) for browser automation.
- [Rich](https://rich.readthedocs.io/en/stable/) for beautiful console output.
- [Inquirer](https://pypi.org/project/inquirer/) for interactive CLI prompts.
- [Cryptography](https://cryptography.io/en/latest/) for secure encryption.

---

Happy analyzing! 📸
