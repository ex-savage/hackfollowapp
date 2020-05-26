from setuptools import find_packages, setup

setup(
    name='hackfollow',
    version='0.0.1',
    description='HN monitoring service',
    author='ex-savage',
    license='MIT',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'hackapp=hackfollow.hack:run'
        ],
    },
)
