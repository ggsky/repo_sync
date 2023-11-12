from setuptools import setup, find_packages

setup(
    name='repo_sync',
    enter_points={'console_scripts': ['repo_sync = repo_sync:main']},
)
