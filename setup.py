from setuptools import find_packages, setup

with open('polyglot/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('= ')[1].strip("'")
            break

setup(
    name='polyglot-bitcoin',
    version=version,
    description='Bitcoin protocols made easy.',
    long_description=open('README.rst', 'r').read(),
    author='AustEcon',
    author_email='AustEcon0922@gmail.com',
    maintainer='AustEcon',
    maintainer_email='AustEcon0922@gmail.com',
    url='https://github.com/AustEcon/polyglot',
    download_url='https://github.com/AustEcon/polyglot/tarball/{}'.format(version),
    license='MIT',

    scripts=['bin/polyglot-upload'],

    keywords=[
        'polyglot',
        'metanet',
        'bitcoin sv',
        'bsv',
        'bitsv',
        'cryptocurrency',
        'payments',
        'tools',
        'wallet',
        'bitcoin',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],

    install_requires=['bitsv', 'requests'],
    extras_require={
        'cli': ('appdirs', 'click', 'privy', 'tinydb'),
        'cache': ('lmdb', ),
    },
    tests_require=['pytest'],
    packages=find_packages(),
)
