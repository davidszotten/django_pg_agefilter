import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-pg-agefilter",
    version = "0.0.4",
    author = "David Szotten",
    author_email = "davidszotten@gmail.com",
    description = "Helpers to leverage postgres's age filter from django",
    install_requires=read('requirements.txt').strip().split('\n'),
    license = "MIT",
    url = "https://github.com/davidszotten/django_pg_agefilter",
    packages=find_packages(exclude=['tests', 'tests.*']),
    long_description=read('README.rst'),
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database',
    ],
    zip_safe=False,
)
