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

"""Provides an HTMLParser subclass to lint an HTML5 file.

It also provides different message classes used to group messages.

Although the class HTML5Parser is public, most people should use instead the
provided lint function.
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

try:
    import HTMLParser
except ImportError:
    import html.parser as HTMLParser
import re
import sys


def unescape(code):
    """Utility function to unescape a string with HTML entities."""
    parser = HTMLParser.HTMLParser()
    return parser.unescape(code)


class UnicodeMixin(object):
    """Mixin class to handle defining the proper __str__/__unicode__ methods."""

    if sys.version_info[0] >= 3:  # Python 3
        def __str__(self):
            return self.__unicode__()
    else:   # Python 2
        def __str__(self):
            return self.__unicode__().encode('utf8')


# pylint: disable=too-few-public-methods,missing-docstring


class Message(UnicodeMixin):
    level = 'Error'
    category = None
    description = None
    message = None

    def __init__(self, line, column):
        self.column = column
        self.line = line

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __unicode__(self):
        return ('%d:%d: %s: %s: %s: %s.' % (self.line,
                                            self.column,
                                            self.level,
                                            self.category,
                                            self.description,
                                            self.message))

    def __repr__(self):
        return str(self)


class DocumentTypeMessage(Message):
    category = 'Document Type'
    description = 'Use HTML5'
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=Document_Type#Document_Type'

    def __init__(self, line, column, declaration):
        Message.__init__(self, line, column)
        self.message = 'Change "%s" to "%s"' % (declaration, '<!DOCTYPE html>')


class EntityReferenceMessage(Message):
    category = 'Entity References'
    description = 'Use the unicode equivalent instead'
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=Entity_References#Entity_References'

    def __init__(self, line, column, entity):
        Message.__init__(self, line, column)
        self.message = 'Change "%s" to "%s"' % (entity, unescape(entity))


class TrailingWhitespaceMessage(Message):
    category = 'Trailing Whitespace'
    description = ('Trailing white spaces are unnecessary and can complicate ' +
                   'diffs')
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=Trailing_Whitespace#Trailing_Whitespace'

    def __init__(self, line, column, whitespace):
        Message.__init__(self, line, column)
        self.message = 'Remove the %s at the end of the line' % repr(whitespace)


class TabMessage(Message):
    category = 'Indentation'
    description = 'Do not use tabs'
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=Indentation#Indentation'

    def __init__(self, line, column):
        Message.__init__(self, line, column)
        self.message = 'Remove the tabs'


class CharsetMessage(Message):
    category = 'Encoding'
    description = 'The meta charset should be set to utf-8'
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=Encoding#Encoding'

    def __init__(self, line, column, charset=None):
        Message.__init__(self, line, column)
        if charset:
            self.message = 'Change the charset from "%s" to "utf-8"' % charset
        else:
            self.message = 'Add the tag <meta charset="utf-8">'


class VoidElementMessage(Message):
    category = 'Document Type'
    description = 'Do not close void elements'
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=Document_Type#Document_Type'

    def __init__(self, line, column, tag, trailing_chars=None):
        Message.__init__(self, line, column)
        if trailing_chars is None:
            self.message = ('Remove the closing %s tag, it is a huge ' +
                            'conceptual error to close it') % tag
        else:
            self.message = ('Remove the trailing "%s" from the %s tag' %
                            (trailing_chars, tag))


class OptionalTagMessage(Message):
    category = 'Optional Tags'
    description = 'Omit optional tags (optional)'
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=Optional_Tags#Optional_Tags'
    level = 'Info'

    def __init__(self, line, column, tag, opening=False):
        Message.__init__(self, line, column)
        tag_type = 'closing'
        if opening:
            tag_type = 'opening'
        self.message = 'You may remove the %s "%s" tag' % (tag_type, tag)


class TypeAttributeMessage(Message):
    category = 'type Attributes'
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=type_Attributes#type_Attributes'

    def __init__(self, line, column, tag):
        Message.__init__(self, line, column)
        default_type = 'unknown'
        if tag in ('link', 'style'):
            default_type = 'text/css'
        elif tag == 'script':
            default_type = 'text/javascript'
        self.description = ('The default type for %s tags is "%s" so it can ' +
                            'be safely omitted') % (tag, default_type)
        self.message = 'Remove the type attribute from the %s tag' % tag


class ConcernsSeparationMessage(Message):
    category = 'Separation of concerns'
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=Separation_of_Concerns#Separation_of_Concerns'

    def __init__(self, line, column, tag, attribute=None):
        Message.__init__(self, line, column)
        if tag == 'script':
            self.description = 'Javascript should be defined in its own file'
            self.message = 'Move the contents of this tag to its own JS file'
        elif tag == 'style':
            self.description = 'CSS should be defined in its own file',
            self.message = 'Move the contents of this tag to its own CSS file'
        elif tag == 'a' and attribute == 'href':
            self.description = 'Javascript should be defined in its own file'
            self.message = ('Move the contents of the "href" attribute to its' +
                            ' own JS file')
        elif attribute == 'style':
            self.description = 'CSS should be defined in its own file'
            self.message = ('Move the contents of the "style" attribute to ' +
                            'its own CSS file')
        elif attribute.startswith('on'):
            self.description = 'Javascript should be defined in its own file'
            self.message = ('Register the handler for "%s" with events in a ' +
                            'JS file') % attribute


class ProtocolMessage(Message):
    category = 'Protocol'
    description = 'Do not specify the protocol unless required'
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=Protocol#Protocol'
    level = 'Warning'

    def __init__(self, line, column, protocol):
        Message.__init__(self, line, column)
        self.message = 'Remove the protocol "%s" from the url' % protocol


class NameMessage(Message):
    category = 'ID and Class Name Delimiters'
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=ID_and_Class_Name_Delimiters#ID_and_Class_Name_Delimiters'

    def __init__(self, line, column, attribute, value):
        Message.__init__(self, line, column)
        self.description = ('The %s names should be lowercase and with ' +
                            'hyphens instead of underscores') % attribute
        self.message = ('Remove the offending characters from the %s "%s"' %
                        (attribute, value))


class CapitalizationMessage(Message):
    category = 'Capitalization'
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=Capitalization#Capitalization'

    TAG_TYPE = {False: 'opening', True: 'closing'}

    def __init__(self, line, column, tag, attribute=None, closing=False):
        Message.__init__(self, line, column)
        if attribute is None:
            self.description = 'Tags should be in lowercase'
            self.message = ('Change the %s tag "%s" to "%s"' %
                            (self.TAG_TYPE[closing], tag, tag.lower()))
        else:
            self.description = 'Attributes should be in lowercase'
            self.message = ('Change the attribute "%s" to "%s"' %
                            (attribute, attribute.lower()))


class QuotationMessage(Message):
    category = 'HTML Quotation Marks'
    description = 'Use only double quotes'
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=HTML_Quotation_Marks#HTML_Quotation_Marks'

    def __init__(self, line, column, quotation=''):
        Message.__init__(self, line, column)
        self.message = 'Change the quotation mark %s to \'"\'' % quotation


class IndentationMessage(Message):
    category = 'Indentation'
    description = 'Use two spaces and no tabs'
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=Indentation#Indentation'

    def __init__(self, line, column, indent, min_indent=0, max_indent=0):
        Message.__init__(self, line, column)
        self.message = ('Was expecting between %d and %d (in multiples of 2) ' +
                        'spaces but got %d') % (min_indent, max_indent, indent)


class FormattingMessage(Message):
    category = 'General Formatting'
    description = ('Use a new line for every block, list, or table element, ' +
                   'and indent every such child element')
    url = 'https://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml?showone=General_Formatting#General_Formatting'

    def __init__(self, line, column, tag):
        Message.__init__(self, line, column)
        self.message = 'Move the opening "%s" to its own line' % tag


class BooleanAttributeMessage(Message):
    category = 'Boolean Attributes'
    description = ('Boolean attributes define their value based on the ' +
                   'presence or abscence of the attribute')
    url = 'http://perfectionkills.com/experimenting-with-html-minifier/#collapse_boolean_attributes'

    def __init__(self, line, column, attribute, value):
        Message.__init__(self, line, column)
        self.message = ('Change \'%s="%s"\' to just \'%s\'' %
                        (attribute, value, attribute))


class InvalidAttributeMessage(Message):
    category = 'Invalid Attributes'

    def __init__(self, line, column, attribute):
        Message.__init__(self, line, column)
        if attribute == 'charset':
            self.description = ('The attribute "charset" applies only to ' +
                                'external resources')
            self.message = 'Remove the "charset" attribute'
            self.url = 'http://perfectionkills.com/optimizing-html/#8_script_charset'
        elif attribute == 'language':
            self.description = ('The attribute "language" was deprecated more' +
                                ' than 10 years ago')
            self.message = 'Remove the "language" attribute'
            self.url = 'http://perfectionkills.com/optimizing-html/#7_script_language_javascript'
        elif attribute == 'name':
            self.description = ('The attribute "name" is no longer required ' +
                                'for anchors')
            self.message = ('Remove the "name" attribute and replace it with ' +
                            'and id if required')
            self.url = 'http://perfectionkills.com/optimizing-html/#5_a_id_name'


class VoidZeroMessage(Message):
    category = 'Javascript Links'
    description = ('It is bad practice to use javascript:void(0) to prevent ' +
                   'the default and it also prevents the use of CSP')
    url = 'http://perfectionkills.com/optimizing-html/#5_href_javascript_void'
    message = ('Change the "href" attribute to href="#" or disable the ' +
               'default by attaching an onclick event to this element and ' +
               'using e.preventdefault()')


class InvalidHandlerMessage(Message):
    category = 'Javascript Links'
    description = 'Event handlers should not have the javascript protocol'
    url = 'http://perfectionkills.com/optimizing-html/#4_onclick_javascript'

    def __init__(self, line, column, attribute):
        Message.__init__(self, line, column)
        self.message = ('Remove the "javascript:" prefix from the "%s" ' +
                        'attribute') % attribute


class HTTPEquivMessage(Message):
    category = 'HTTP Equiv'
    description = 'HTML5 restricts the values of http-equiv'
    url = 'http://www.w3.org/TR/html5/document-metadata.html#pragma-directives'

    def __init__(self, line, column, http_equiv):
        Message.__init__(self, line, column)
        http_equiv = http_equiv.lower()
        if http_equiv == 'content-language':
            self.message = 'Specify the language in the html tag, see '
            self.message += 'http://www.w3.org/International/questions/qa-http-and-lang.en#answer'
        elif http_equiv == 'content-type':
            self.message = 'Replace this by <meta charset="utf-8">'
        elif http_equiv == 'set-cookie':
            self.message = ('The http-equiv "%s" directive is non conformant,' +
                            ' avoid it') % http_equiv
        elif http_equiv in ('pragma', 'expires'):
            self.message = (
                'HTML5 does not allow the http-equiv "%s" directive. To cache' +
                ' you need to use the HTTP headers or Appcache with a ' +
                'manifest file') % http_equiv
        else:
            self.message = ('HTML5 does not allow the http-equiv "%s" ' +
                            'directive') % http_equiv


class ExtraWhitespaceMessage(Message):
    category = 'Extra whitespace'
    description = 'Use whitespaces only where expected and be consistent'

    def __init__(self, line, column):
        Message.__init__(self, line, column)
        self.message = 'Remove the extra whitespaces'


# pylint: enable=too-few-public-methods,missing-docstring


TRAILING_WHITESPACE_PATTERN = re.compile(r'([\t ]+)[\r\n]')
TAB_PATTERN = re.compile(r'\t+')
SELF_CLOSING_TAG_PATTERN = re.compile('([\t ]*/)>')
VOID_ZERO_PATTERN = re.compile(r'^javascript:\s*void\s*\(\s*0\s*\)\s*;?$',
                               flags=re.IGNORECASE)

VOID_TAGS = frozenset((
    'br', 'hr', 'img', 'input', 'link', 'meta', 'area', 'base', 'col',
    'command', 'embed', 'keygen', 'param', 'source', 'track', 'wbr'))
OPTIONAL_CLOSING_TAGS = frozenset((
    'html', 'head', 'body', 'p', 'dt', 'dd', 'li', 'option', 'thead', 'th',
    'tbody', 'tr', 'td', 'tfoot', 'colgroup'))
OPTIONAL_OPENING_TAGS = frozenset(('body', 'head', 'html', 'tbody'))

VALID_ENTITIES = frozenset((
    'lt', 'gt', 'amp', 'quot', 'nbsp', 'ensp', 'emsp', 'thinsp'))

VALID_HTTP_EQUIV = frozenset((
    'refresh', 'default-style', 'x-ua-compatible', ''))

# List taken from
# https://developer.mozilla.org/en-US/docs/Web/HTML/Block-level_elements
BLOCK_TAGS = frozenset((
    'address', 'article', 'aside', 'audio', 'blockquote', 'canvas', 'dd', 'div',
    'dl', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2',
    'h3', 'h4', 'h5', 'h6', 'header', 'hgroup', 'hr', 'noscript', 'ol',
    'output', 'p', 'pre', 'section', 'table', 'tfoot', 'ul', 'video'))
# List extracted from
# https://developer.mozilla.org/en/docs/Web/Guide/HTML/HTML5/HTML5_element_list#Grouping_content
LIST_TAGS = frozenset(('ol', 'ul', 'li', 'dl', 'dt', 'dd'))
# List taken from
# https://developer.mozilla.org/en/docs/Web/Guide/HTML/HTML5/HTML5_element_list#Tabular_data
TABLE_TAGS = frozenset((
    'table', 'caption', 'colgroup', 'col', 'tbody', 'thead', 'tfoot', 'tr',
    'td', 'th'))
NEWLINE_TAGS = BLOCK_TAGS | LIST_TAGS | TABLE_TAGS

# List obtained using the command:
# curl -s "http://www.w3.org/TR/html51/single-page.html" |
# egrep "^\s+attribute boolean" | sed "s|^.*>\(.*\)</.*>;|'\1', |g" |
# tr '[:upper:]' '[:lower:]' | sort -u | tr -d '\n'
BOOLEAN_ATTRIBUTES = frozenset((
    'allowfullscreen', 'async', 'autofocus', 'autoplay', 'checked', 'compact',
    'controls', 'declare', 'default', 'defaultchecked', 'defaultmuted',
    'defaultselected', 'defer', 'disabled', 'draggable', 'enabled',
    'formnovalidate', 'hidden', 'indeterminate', 'inert', 'ismap', 'itemscope',
    'loop', 'multiple', 'muted', 'nohref', 'noresize', 'noshade', 'novalidate',
    'nowrap', 'open', 'pauseonexit', 'readonly', 'required', 'reversed',
    'scoped', 'seamless', 'selected', 'sortable', 'spellcheck', 'translate',
    'truespeed', 'typemustmatch', 'visible'))


def get_line_column(data, line, column, position):
    """Returns the line and column of the given position in the string.

    Column is 1-based, that means, that the first character in a line has column
    equal to 1. A line with n character also has a n+1 column, which sits just
    before the newline.

    Args:
      data: the original string.
      line: the line at which the string starts.
      column: the column at which the string starts.
      position: the position within the string. It is 0-based.

    Returns:
      A tuple (line, column) with the offset of the position.
    """
    data = data[:position]
    toks = data.splitlines()
    if not toks or data[-1] in '\n\r':
        toks.append('')
    if len(toks) > 1:
        return line + len(toks) - 1, 1 + len(toks[-1])
    else:
        return line, column + position


def get_attribute_line_column(tag_definition, line, column, attribute):
    """Returns the line and column of the provided attribute.

    Args:
        tag_definition: str with the definition of the tag.
        line: line where the tag starts.
        column: column where the tag starts (1-based).
        attribute: str representing the attribute to find.

    Return:
       A (line, column) tuple representing the position of the attribute.
    """
    for match in HTMLParser.attrfind.finditer(tag_definition):
        if match.group(1).lower() == attribute:
            return get_line_column(tag_definition, line, column, match.start(1))

    assert False, 'Could not find the requested attribute %s' % attribute


def get_value_line_column(tag_definition, line, column, attribute):
    """Returns the line and column of the value of the provided attribute.

    Args:
        tag_definition: str with the definition of the tag.
        line: line where the tag starts.
        column: column where the tag starts (1-based).
        attribute: str representing the attribute for which we want its value.

    Return:
       A (line, column) tuple representing the position of the value.
    """
    for match in HTMLParser.attrfind.finditer(tag_definition):
        if match.group(1).lower() == attribute:
            if not match.group(3):
                pos = match.end(1)
            elif match.group(3)[0] in '"\'':
                pos = match.start(3) + 1
            else:
                pos = match.start(3)
            return get_line_column(tag_definition, line, column, pos)

    assert False, 'Could not find the requested attribute %s' % attribute


# pylint: disable=too-many-public-methods
class HTML5Linter(HTMLParser.HTMLParser):
    """Lints an HTML5 file.

    It adds the messages property to get a list of all found issues. This list
    will always be sorted by line and column. There's no way to filter out
    these messages, if you want that use the provided lint function.

    It changes somewhat the the usage of the base class, as it will call feed
    and close directly in the constructor.
    """
    def __init__(self, html):
        self._messages = []

        # Variables used to get the indentation
        self._last_data = ''
        self._last_data_position = (0, 1)
        self._last_indent = 0

        # Variables used to check if a charset tag should be required.
        self._first_meta_line_col = None
        self._after_head_line_col = None
        self._has_charset = False

        # Variables to extend the feature set of HTMLParser.
        self._endtag_text = None

        HTMLParser.HTMLParser.__init__(self)

        # In case we are dealing with Python 3, set it to non-strict mode.
        if hasattr(self, 'strict'):
            self.strict = False

        self.feed(html)
        self.close()

    @property
    def messages(self):
        """Returns a sorted list of the found messages."""
        self._messages.sort(key=lambda m: (m.line, m.column))
        return self._messages

    def getline(self):
        """Returns the current line of the parser."""
        return self.getpos()[0]

    def getcolumn(self):
        """Returns the current column (1-based) of the parser."""
        return self.getpos()[1] + 1

    def get_attribute_line_column(self, attribute):
        """Returns the line and column of the attribute.

        It only makes sense to call this method within an opening tag.
        """
        return get_attribute_line_column(self.get_starttag_text(),
                                         self.getline(),
                                         self.getcolumn(),
                                         attribute)

    def get_value_line_column(self, attribute):
        """Returns the line and column of the value of the attribute.

        It only makes sense to call this method within an opening tag.
        """
        return get_value_line_column(self.get_starttag_text(),
                                     self.getline(),
                                     self.getcolumn(),
                                     attribute)

    def handle_decl(self, decl):
        if decl.strip() != 'DOCTYPE html':
            self._messages.append(
                DocumentTypeMessage(line=self.getline(),
                                    column=self.getcolumn(),
                                    declaration='<!%s>' % decl))

    def handle_entityref(self, name):
        if name not in VALID_ENTITIES:
            entity = '&%s;' % name
            self._messages.append(
                EntityReferenceMessage(line=self.getline(),
                                       column=self.getcolumn(),
                                       entity=entity))

    def handle_charref(self, name):
        entity = '&#%s;' % name
        self._messages.append(
            EntityReferenceMessage(line=self.getline(),
                                   column=self.getcolumn(),
                                   entity=entity))

    def handle_data(self, data):
        self._last_data = data
        self._last_data_position = self.getline(), self.getcolumn()
        for match in TRAILING_WHITESPACE_PATTERN.finditer(data):
            line, column = get_line_column(
                data, self.getline(), self.getcolumn(), match.start())
            self._messages.append(
                TrailingWhitespaceMessage(line=line,
                                          column=column,
                                          whitespace=match.group(1)))

        for match in TAB_PATTERN.finditer(data):
            line, column = get_line_column(
                data, self.getline(), self.getcolumn(), match.start())
            self._messages.append(TabMessage(line=line, column=column))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if getattr(self, '_handle_%s_starttag' % tag, None):
            getattr(self, '_handle_%s_starttag' % tag)(attrs)

        self._handle_style_attribute(tag, attrs)
        self._handle_on_attributes(tag, attrs)
        self._handle_href_src_attributes(tag, attrs)
        self._handle_id_attribute(tag, attrs)
        self._handle_class_attribute(tag, attrs)

        self._check_optional_opening_tag(tag, attrs)
        self._check_starttag_capitalization(tag)
        self._check_attributes_case_quotation_entities(tag, attrs)

        self._check_boolean_attributes(attrs)

        self._check_tags_in_newline(tag)
        # This needs to be after as it erases self._last_data, which is needed
        # to get the indentation.
        self._check_indentation()
        self._check_whitespaces(opening=True)

        # Reset the _end_tag text, so to prevent to consider a self closing tag
        # as a closing one.
        self._endtag_text = None

    def _handle_head_starttag(self, unused_attrs):
        self._after_head_line_col = get_line_column(
            self.get_starttag_text(), self.getline(), self.getcolumn(),
            len(self.get_starttag_text()))

    def _handle_meta_starttag(self, attrs):
        if not self._first_meta_line_col:
            self._first_meta_line_col = self.getline(), self.getcolumn()

        if attrs.get('http-equiv', '').lower() not in VALID_HTTP_EQUIV:
            line, column = self.get_attribute_line_column('http-equiv')
            self._messages.append(
                HTTPEquivMessage(line=line,
                                 column=column,
                                 http_equiv=attrs['http-equiv']))

        if 'charset' not in attrs:
            return

        self._has_charset = True
        if attrs['charset'] != 'utf-8':
            line, column = self.get_value_line_column('charset')
            self._messages.append(
                CharsetMessage(line=line,
                               column=column,
                               charset=attrs['charset']))

    def _handle_link_starttag(self, attrs):
        if attrs.get('type') == 'text/css':
            line, column = self.get_attribute_line_column('type')
            self._messages.append(
                TypeAttributeMessage(line=line, column=column, tag='link'))

    def _handle_script_starttag(self, attrs):
        if attrs.get('type') == 'text/javascript':
            line, column = self.get_attribute_line_column('type')
            self._messages.append(
                TypeAttributeMessage(line=line, column=column, tag='script'))
        if 'src' not in attrs:
            self._messages.append(
                ConcernsSeparationMessage(line=self.getline(),
                                          column=self.getcolumn(),
                                          tag='script'))
            if 'charset' in attrs:
                line, column = self.get_attribute_line_column('charset')
                self._messages.append(
                    InvalidAttributeMessage(line=line,
                                            column=column,
                                            attribute='charset'))
        if 'language' in attrs:
            line, column = self.get_attribute_line_column('language')
            self._messages.append(
                InvalidAttributeMessage(line=line,
                                        column=column,
                                        attribute='language'))

    def _handle_style_starttag(self, attrs):
        self._messages.append(
            ConcernsSeparationMessage(line=self.getline(),
                                      column=self.getcolumn(),
                                      tag='style'))
        if attrs.get('type') == 'text/css':
            line, column = self.get_attribute_line_column('type')
            self._messages.append(
                TypeAttributeMessage(line=line, column=column, tag='style'))

    def _handle_a_starttag(self, attrs):
        if VOID_ZERO_PATTERN.match(attrs.get('href', '').strip()):
            line, column = self.get_value_line_column('href')
            self._messages.append(
                VoidZeroMessage(line=line, column=column))
        elif attrs.get('href', '').strip().lower().startswith('javascript:'):
            line, column = self.get_value_line_column('href')
            self._messages.append(
                ConcernsSeparationMessage(line=line,
                                          column=column,
                                          tag='a',
                                          attribute='href'))
        if 'name' in attrs:
            line, column = self.get_attribute_line_column('name')
            self._messages.append(
                InvalidAttributeMessage(line=line,
                                        column=column,
                                        attribute='name'))

    def _handle_style_attribute(self, tag, attrs):
        if 'style' in attrs:
            line, column = self.get_attribute_line_column('style')
            self._messages.append(
                ConcernsSeparationMessage(line=line,
                                          column=column,
                                          tag=tag,
                                          attribute='style'))

    def _handle_on_attributes(self, tag, attrs):
        for attr in attrs:
            if attr.lower().startswith('on'):
                line, column = self.get_attribute_line_column(attr)
                self._messages.append(
                    ConcernsSeparationMessage(line=line,
                                              column=column,
                                              tag=tag,
                                              attribute=attr))

                if attrs[attr].strip().lower().startswith('javascript:'):
                    line, column = self.get_value_line_column(attr)
                    self._messages.append(
                        InvalidHandlerMessage(line=line,
                                              column=column,
                                              attribute=attr))

    def _handle_href_src_attributes(self, unused_tag, attrs):
        attr = None
        if 'src' in attrs:
            attr = 'src'
        elif 'href' in attrs:
            attr = 'href'
        url = attrs.get(attr, '')
        match = re.match(r'^(http[s]?:)', url)
        if not match:
            return

        protocol = match.group(0)
        line, column = self.get_value_line_column(attr)
        self._messages.append(
            ProtocolMessage(line=line,
                            column=column,
                            protocol=protocol))

    def _handle_id_attribute(self, unused_tag, attrs):
        name = attrs.get('id', '')
        if not re.match(r'^[a-z0-9-]*$', name):
            line, column = self.get_value_line_column('id')
            self._messages.append(
                NameMessage(line=line,
                            column=column,
                            attribute='id',
                            value=name))

    def _handle_class_attribute(self, unused_tag, attrs):
        name = attrs.get('class', '')
        if not re.match(r'^[a-z0-9 -]*$', name):
            line, column = self.get_value_line_column('class')
            self._messages.append(
                NameMessage(line=line,
                            column=column,
                            attribute='class',
                            value=name))

    def _check_optional_opening_tag(self, tag, attrs):
        if tag in OPTIONAL_OPENING_TAGS and not attrs:
            self._messages.append(
                OptionalTagMessage(line=self.getline(),
                                   column=self.getcolumn(),
                                   tag=tag,
                                   opening=True))

    def _check_starttag_capitalization(self, tag):
        original_def = self.get_starttag_text()
        original_tag = original_def[1:len(tag) + 1]
        # We do not use islower() due to http://bugs.python.org/issue13822.
        if original_tag != original_tag.lower():
            self._messages.append(
                CapitalizationMessage(line=self.getline(),
                                      column=self.getcolumn() + 1,
                                      tag=original_tag))

    def _check_attributes_case_quotation_entities(self, tag, unused_attrs):
        original_def = self.get_starttag_text()
        for match in HTMLParser.attrfind.finditer(original_def, len(tag) + 1):
            # We do not use islower() due to http://bugs.python.org/issue13822.
            if match.group(1) != match.group(1).lower():
                line, column = self.get_attribute_line_column(
                    match.group(1).lower())
                self._messages.append(
                    CapitalizationMessage(line=line,
                                          column=column,
                                          tag=tag,
                                          attribute=match.group(1)))
            if not match.group(3):
                continue
            if not match.group(3).startswith('"'):
                line, column = get_line_column(
                    original_def, self.getline(), self.getcolumn(),
                    match.start(3))
                quotation = ''
                if match.group(3).startswith('\''):
                    quotation = '\''
                self._messages.append(
                    QuotationMessage(line=line,
                                     column=column,
                                     quotation=quotation))

            # Notify ourselves of any entities found on the attributes
            current_pos = self.getpos()
            line, column = self.getline(), self.getcolumn()
            for entity_match in HTMLParser.entityref.finditer(match.group(3)):
                if not entity_match.group().endswith(';'):
                    continue
                self.line, self.offset = get_line_column(
                    original_def, line, column,
                    entity_match.start(0) + match.start(3))
                self.offset -= 1
                self.handle_entityref(entity_match.group(1))

            for entity_match in HTMLParser.charref.finditer(match.group(3)):
                if not entity_match.group().endswith(';'):
                    continue
                self.line, self.offset = get_line_column(
                    original_def, line, column,
                    entity_match.start(0) + match.start(3))
                self.offset -= 1
                self.handle_charref(entity_match.group(0)[2:-1])

            # Line is defined in the base class.
            # pylint: disable=attribute-defined-outside-init
            self.line, self.offset = current_pos
            # pylint: enable=attribute-defined-outside-init

    def handle_endtag(self, tag):
        self._check_endtag_capitalization()

        self._check_indentation()
        self._check_whitespaces(opening=False)

        if tag in VOID_TAGS:
            trailing_chars = None
            line, column = self.getline(), self.getcolumn()
            match = SELF_CLOSING_TAG_PATTERN.search(self.get_starttag_text())
            if match:
                trailing_chars = match.group(1)
                line, column = get_line_column(
                    self.get_starttag_text(), line, column, match.start(1))
            self._messages.append(
                VoidElementMessage(line=line,
                                   column=column,
                                   tag=tag,
                                   trailing_chars=trailing_chars))
        elif tag in OPTIONAL_CLOSING_TAGS:
            self._messages.append(
                OptionalTagMessage(line=self.getline(),
                                   column=self.getcolumn(),
                                   tag=tag))

    def _check_endtag_capitalization(self):
        endtag = self.get_endtag_text()
        # We do not use islower() due to http://bugs.python.org/issue13822.
        if endtag and endtag != endtag.lower():
            match = HTMLParser.endtagfind.match(endtag)  # </ + tag + >
            original_endtag = match.group(1)
            self._messages.append(
                CapitalizationMessage(line=self.getline(),
                                      column=self.getcolumn() + 2,
                                      tag=original_endtag,
                                      closing=True))

    def close(self):
        if (not self._has_charset and
                (self._first_meta_line_col or self._after_head_line_col)):
            line, column = (self._first_meta_line_col or
                            self._after_head_line_col)
            self._messages.append(CharsetMessage(line=line, column=column))

    def _check_indentation(self):
        indentation = self._get_indentation()
        if indentation is None:
            return

        # Argg, given that we don't implement the opening and closing tags
        # HTML5 logic, we need to allow any indentation that is multiple of two
        # between 0 and last_indent + 2. This is to prevent false positives.
        if indentation not in range(self._last_indent + 2, -1, -2):
            self._messages.append(
                IndentationMessage(line=self.getline(),
                                   column=1,
                                   indent=indentation,
                                   max_indent=self._last_indent + 2))
            # Normalize the indentation, so to minimize subsequent indents.
            if indentation > self._last_indent + 2:
                indentation = self._last_indent + 2
            elif indentation > self._last_indent:
                indentation += 1
            else:
                indentation -= 1

        self._last_indent = indentation
        self._last_data = None

    def _check_tags_in_newline(self, tag):
        if tag in NEWLINE_TAGS and self._get_indentation() is None:
            self._messages.append(
                FormattingMessage(line=self.getline(),
                                  column=self.getcolumn(),
                                  tag=tag))

    def _check_boolean_attributes(self, attrs):
        for attr, value in attrs.items():
            if attr in BOOLEAN_ATTRIBUTES and value is not None:
                line, column = self.get_attribute_line_column(attr)
                self._messages.append(
                    BooleanAttributeMessage(line=line,
                                            column=column,
                                            attribute=attr,
                                            value=value))

    def _check_whitespaces(self, opening):
        tag_pattern = re.compile(
            r'</?(?P<start>\s*)\w+(.*?)(\s*/|(?P<end>\s*))>',
            flags=re.DOTALL)
        attribute_pattern = re.compile(
            r'([\n\r]\s*|\s)(?P<before_attr>\s*)\w+' +
            r'((?P<after_attr>\s*)=(?P<before_value>\s*))?',
            flags=re.MULTILINE | re.DOTALL)
        if opening:
            original_def = self.get_starttag_text()
        else:
            original_def = self.get_endtag_text()
        if original_def is None:
            return

        match = tag_pattern.match(original_def)
        assert match is not None, 'the regular expression is invalid'

        for group_name in ('start', 'end'):
            if match.group(group_name):
                line, column = get_line_column(
                    original_def, self.getline(), self.getcolumn(),
                    match.start(group_name))
                self._messages.append(
                    ExtraWhitespaceMessage(line=line, column=column))

        for attr_match in attribute_pattern.finditer(original_def,
                                                     match.start(2)):
            for group_name in ('before_attr', 'after_attr', 'before_value'):
                if attr_match.group(group_name):
                    line, column = get_line_column(
                        original_def, self.getline(), self.getcolumn(),
                        attr_match.start(group_name))
                    self._messages.append(
                        ExtraWhitespaceMessage(line=line, column=column))

    # Overrides to support extra functions
    def parse_endtag(self, i):
        """Stores the endtag and delegates to the original method."""
        match = HTMLParser.endtagfind.match(self.rawdata, i)  # </ + tag + >
        self._endtag_text = None
        if match:
            self._endtag_text = match.group(0)

        return HTMLParser.HTMLParser.parse_endtag(self, i)

    def get_endtag_text(self):
        """Returns the last defined endtag."""
        return self._endtag_text

    # Utility functions
    def _get_indentation(self):
        """Returns the indentation of an opening or closing tag.

        It works by storing the last data seen and checking that there are only
        spaces in the last line.

        Tabs are assumed to be equivalent to two spaces.
        """
        if self._last_data is None:
            return None

        toks = self._last_data.splitlines()
        # This is required to actually get the content of all the lines.
        # The self._last_data[-1] is guaranteed to be defined as toks is not
        # empty.
        if not toks or self._last_data[-1] in '\n\r':
            toks.append('')
        if len(toks) == 1 and self._last_data_position[1] != 1:
            return None

        potential_indent = toks[-1].replace('\t', '  ')
        indent = ' ' * len(potential_indent)
        if indent == potential_indent:
            return len(indent)

        return None


def lint(html, exclude=None):
    """Lints and HTML5 file.

    Args:
      html: str the contents of the file.
      exclude: optional iterable with the Message classes to be ommited from the
               output.
    """
    exclude = exclude or []
    messages = [m.__unicode__() for m in HTML5Linter(html).messages
                if not isinstance(m, tuple(exclude))]
    return '\n'.join(messages)
