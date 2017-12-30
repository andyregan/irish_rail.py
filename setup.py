from setuptools import setup, find_packages

setup(
    name='irish_rail',
    version='0.0.1',
    description='Python library to get the real-time transport information (RTPI) from Irish Rail',
    keywords='irish rail RTPI',
    author='Andrew Regan',
    author_email='andrewjregan@gmail.com',
    platforms=["any"],
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'requests',
        'geopy'
    ]
)
