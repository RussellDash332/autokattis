# autokattis

Kattis scraper, updated as of May 2023 after the major UI/UX change.

## Usage

```
pip install -r requirements.txt
echo "USER = <user>" >> env.py
echo "PASSWORD = <password>" >> env.py
python main.py
```

- `<user>` can be your Kattis username or email **as a single-quoted Python string**, e.g. `'helloworld'` or `'helloworld@gmail.com'`.
- `<password>` is your Kattis account's password **as a single-quoted Python string**, e.g. `'asdf'`.

See `env.py.example` for an example of doing the `echo` parts manually.

## Contributing

asdf