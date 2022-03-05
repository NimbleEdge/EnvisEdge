from setuptools import setup

setup(
    name='envisedge',
    version='0.0.1',
    description='A simulator for federated learning',
    url='https://github.com/NimbleEdge/envisedge',
    author='Varun Kumar Khare',
    author_email='vkkhare@nimbleedge.ai',
    license='Apache 2-clause',
    packages=['fedrec','fl_strategies','experiments'],
    install_requires=['numpy'],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.8',
    ],
)