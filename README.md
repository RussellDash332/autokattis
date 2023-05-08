# autokattis

Kattis scraper, updated as of May 2023 after the major UI/UX change.

## Usage

1. Run `pip install -r requirements.txt` to install the Python packages required.
1. Create a new file called `env.py` and add these two lines.

    ```python
    USER = <username>
    PASSWORD = <password>
    ```

    where `<username>` is your Kattis username/email and `<password>` is your Kattis account password. Both should be provided as **Python strings**.
1. Run `python main.py`.

## Useful References

- Old UI Kattis API wrapper: https://github.com/terror/kattis-api

    > Most of the work in `autokattis` is heavily inspired and motivated by this repository.

- Kattis official CLI tool: https://github.com/Kattis/kattis-cli

    > Since Kattis has provided an official tool to automate submissions, there won't be such feature in `autokattis`.

## Contributing

asdf