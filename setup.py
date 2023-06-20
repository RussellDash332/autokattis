from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='autokattis',
    version='1.4.4',
    description='Updated Kattis API wrapper',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=find_packages(),
    author='Russell Saerang',
    author_email='russellsaerang@gmail.com',
    keywords=['Kattis'],
    install_requires = [
        'requests',
        'beautifulsoup4',
        'lxml',
        'pandas',
        'matplotlib',
        'seaborn',
        'thefuzz',
        'thefuzz[speedup]',
    ],
    url='https://github.com/RussellDash332/autokattis',
    download_url='https://pypi.org/project/autokattis/'
)

if __name__ == '__main__':
    setup(**setup_args, include_package_data=True)