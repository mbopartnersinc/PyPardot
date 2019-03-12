from setuptools import setup


setup(
    name="PyPardot",
    version="0.3",
    author="Rob Young",
    author_email="ryoung@gmbopartners.com",
    description=("API wrapper for Pardot marketing automation software. 90% of this is originally joshgeller's "
                 "[https://github.com/joshgeller/PyPardot]"),
    keywords="pardot",
    url="https://github.com/ryoung-mbo/PyPardot",
    packages=['pypardot', 'pypardot.objects'],
    install_requires=['requests'],
)
