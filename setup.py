# Copyright 2014 Deezer (http://www.deezer.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages


setup(
    name='html-linter',
    version='0.1.4',
    description='Lints an HTML5 file using Google\'s style guide',
    long_description=open('README.rst').read(),
    author='Sebastian Kreft - Deezer',
    author_email='skreft@deezer.com',
    url='http://github.com/deezer/html-linter',
    py_modules=['html_linter'],
    install_requires=['template-remover', 'docopt==0.6.1'],
    tests_require=['nose>=1.3'],
    scripts=['scripts/html_lint.py'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
    ],
)
