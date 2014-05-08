#!/usr/bin/env python
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

"""html_lint.py

This HTML5 linter follows the style guide open sourced by Google
https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml.

It also extends the guide with some rules defined by the project
https://github.com/kangax/html-minifier.

This software is released under the Apache License. Copyright Deezer 2014.

Usage:
  html5_lint.py [--disable=DISABLE] FILENAME
  html5_lint.py (-h | --help)
  html5_lint.py --version

Options:
  -h --help        Show this screen.
  --version        Show version.
  --disable=checks A comma separated list of checks to disable. Valid names are:
                   doctype, entities, trailing_whitespace, tabs, charset,
                   void_element, optional_tag, type_attribute,
                   concerns_separation, protocol, names,
                   capitalization, quotation, indentation, formatting,
                   boolean_attribute, invalid_attribute, void_zero,
                   invalid_handler, http_equiv, extra_whitespace.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import io
import sys

import docopt

import html_linter
import template_remover

_DISABLE_MAP = {
    'doctype': html_linter.DocumentTypeMessage,
    'entities': html_linter.EntityReferenceMessage,
    'trailing_whitespace': html_linter.TrailingWhitespaceMessage,
    'tabs': html_linter.TabMessage,
    'charset': html_linter.CharsetMessage,
    'void_element': html_linter.VoidElementMessage,
    'optional_tag': html_linter.OptionalTagMessage,
    'type_attribute': html_linter.TypeAttributeMessage,
    'concerns_separation': html_linter.ConcernsSeparationMessage,
    'protocol': html_linter.ProtocolMessage,
    'names': html_linter.NameMessage,
    'capitalization': html_linter.CapitalizationMessage,
    'quotation': html_linter.QuotationMessage,
    'indentation': html_linter.IndentationMessage,
    'formatting': html_linter.FormattingMessage,
    'boolean_attribute': html_linter.BooleanAttributeMessage,
    'invalid_attribute': html_linter.InvalidAttributeMessage,
    'void_zero': html_linter.VoidZeroMessage,
    'invalid_handler':  html_linter.InvalidHandlerMessage,
    'http_equiv':  html_linter.HTTPEquivMessage,
    'extra_whitespace': html_linter.ExtraWhitespaceMessage,
}


__VERSION__ = '0.1'


def main():
    """Entry point for the HTML5 Linter."""

    # Wrap sys stdout for python 2, so print can understand unicode.
    if sys.version_info[0] < 3:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

    options = docopt.docopt(__doc__,
                            help=True,
                            version='html5_lint v%s' % __VERSION__)

    disable_str = options['--disable'] or ''
    disable = disable_str.split(',')

    invalid_disable = set(disable) - set(_DISABLE_MAP.keys()) - set(('',))
    if invalid_disable:
        sys.stderr.write(
            'Invalid --disable arguments: %s\n\n' % ', '.join(invalid_disable))
        sys.stderr.write(__doc__)
        return 1

    exclude = [_DISABLE_MAP[d] for d in disable if d in _DISABLE_MAP]
    clean_html = template_remover.clean(io.open(options['FILENAME']).read())
    print(html_linter.lint(clean_html, exclude=exclude))

    return 0

if __name__ == '__main__':
    sys.exit(main())
