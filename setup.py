from setuptools import setup

setup(
    name='isetlx',
    version='1.0',
    packages=['isetlx'],
    description='Python wrapper kernel for SetlX',
    author='Georg Reich',
    url='https://github.com/1b15/iSetlX',
    install_requires=[
        'jupyter_client', 'IPython', 'ipykernel'
    ],
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)