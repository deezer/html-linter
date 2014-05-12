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

"""Tests for the html_linter module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import unittest

import html_linter


# pylint: disable=too-many-public-methods,protected-access


class TestHTML5Linter(unittest.TestCase):
    def test_doctype(self):
        # Non HTML5 doctype
        self.assertEquals(
            [html_linter.DocumentTypeMessage(
                line=1, column=1, declaration='<!DOCTYPE html PUBLIC>')],
            html_linter.HTML5Linter('<!DOCTYPE html PUBLIC>').messages
        )
        # Extra whitespace
        self.assertEquals(
            [html_linter.DocumentTypeMessage(
                line=1, column=1, declaration='<!DOCTYPE  html>')],
            html_linter.HTML5Linter('<!DOCTYPE  html>').messages
        )
        # The right doctype
        self.assertEquals(
            [],
            html_linter.HTML5Linter('<!DOCTYPE html>').messages
        )

    def test_entity_references(self):
        self.assertEquals(
            [html_linter.EntityReferenceMessage(
                line=1, column=2, entity='&aacute;')],
            html_linter.HTML5Linter(' &aacute; ').messages
        )

        self.assertEquals(
            [],
            html_linter.HTML5Linter(' &lt; &gt; &nbsp; &amp; ').messages
        )

    def test_entity_references_in_attributes(self):
        self.assertEquals(
            [html_linter.EntityReferenceMessage(
                line=1, column=11, entity='&aacute;')],
            html_linter.HTML5Linter('<a href=" &aacute; ">').messages
        )

        self.assertEquals(
            [],
            html_linter.HTML5Linter(
                '<a href="&lt; &gt; &nbsp; &amp;">').messages
        )

    def test_entity_reference_must_have_semicolon(self):
        self.assertEquals(
            [],
            html_linter.HTML5Linter(
                '<a href="foo?foo=foo&bar=bar&baz=baz">').messages
        )
        self.assertEquals(
            [],
            html_linter.HTML5Linter('<a href=" &aacute= ">').messages
        )

    def test_char_references(self):
        self.assertEquals(
            [html_linter.EntityReferenceMessage(
                line=1, column=2, entity='&#32;')],
            html_linter.HTML5Linter(' &#32; ').messages
        )

    def test_char_references_in_attributes(self):
        self.assertEquals(
            [html_linter.EntityReferenceMessage(
                line=1, column=11, entity='&#32;')],
            html_linter.HTML5Linter('<a href=" &#32; ">').messages
        )

    def test_char_reference_must_have_semicolon(self):
        self.assertEquals(
            [],
            html_linter.HTML5Linter('<a href=" &#32= ">').messages
        )

    def test_trailing_whitespace(self):
        self.assertEquals(
            [html_linter.TrailingWhitespaceMessage(
                line=1, column=4, whitespace=' ')],
            html_linter.HTML5Linter('foo \n').messages
        )
        self.assertEquals(
            [html_linter.TrailingWhitespaceMessage(
                line=1, column=4, whitespace=' '),
             html_linter.TrailingWhitespaceMessage(
                line=2, column=5, whitespace='  ')],
            html_linter.HTML5Linter('foo \nbarz  \n').messages
        )
        self.assertEquals(
            [html_linter.TrailingWhitespaceMessage(
                line=1, column=4, whitespace='\t \t'),
             html_linter.TabMessage(line=1, column=4),
             html_linter.TabMessage(line=1, column=6)],
            html_linter.HTML5Linter('foo\t \t\r').messages
        )
        # Only complaint before a newline
        self.assertEquals(
            [],
            html_linter.HTML5Linter('a  ').messages
        )

    def test_tabs(self):
        self.assertEquals(
            [html_linter.TabMessage(line=1, column=3)],
            html_linter.HTML5Linter('  \t\t').messages
        )
        self.assertEquals(
            [html_linter.TabMessage(line=1, column=3),
             html_linter.TabMessage(line=2, column=1)],
            html_linter.HTML5Linter('  \ta\n\ta').messages
        )

    def test_charset(self):
        self.assertEquals(
            [html_linter.CharsetMessage(line=1, column=16, charset='foo')],
            html_linter.HTML5Linter('<meta charset="foo">').messages
        )
        self.assertEquals(
            [html_linter.CharsetMessage(line=1, column=16, charset='UTF-8')],
            html_linter.HTML5Linter('<meta charset="UTF-8">').messages
        )
        self.assertEquals(
            [],
            html_linter.HTML5Linter('<meta charset="utf-8">').messages
        )

    def test_charset_not_present(self):
        self.assertEquals(
            [html_linter.CharsetMessage(line=1, column=1)],
            html_linter.HTML5Linter('<meta description="foo">').messages
        )
        # We add the attribute so the optional tag check is not raised
        self.assertEquals(
            [html_linter.CharsetMessage(line=2, column=22)],
            html_linter.HTML5Linter('\n<head data-lang="en">').messages
        )

    def test_close_void_tags(self):
        self.assertEquals(
            [html_linter.VoidElementMessage(
                line=1, column=4, tag='br', trailing_chars='/'),
             html_linter.VoidElementMessage(
                line=1, column=20, tag='img', trailing_chars='/'),
             html_linter.VoidElementMessage(
                line=2, column=6, tag='img')],
            html_linter.HTML5Linter(
                '<br/><img src="foo"/>\n<img></img>').messages
        )

    def test_close_optional_tags(self):
        self.assertEquals(
            [html_linter.OptionalTagMessage(line=1, column=7, tag='p'),
             html_linter.OptionalTagMessage(line=2, column=3, tag='body'),
             html_linter.OptionalTagMessage(line=3, column=1, tag='html')],
            html_linter.HTML5Linter('<p>foo</p>\n  </body>\n</html>').messages
        )

    def test_open_optional_tag(self):
        self.assertEquals(
            [html_linter.OptionalTagMessage(
                line=1, column=1, tag='html', opening=True),
             html_linter.OptionalTagMessage(
                line=1, column=10, tag='body', opening=True)],
            html_linter.HTML5Linter('<html>foo<body>').messages
        )
        self.assertEquals(
            [],
            html_linter.HTML5Linter(
                '<html data-lang="en">foo<body data-lang="en">').messages
        )

    def test_link_type(self):
        self.assertEquals(
            [html_linter.TypeAttributeMessage(line=1, column=7, tag='link')],
            html_linter.HTML5Linter(
                '<link type="text/css" href="foo.css">').messages
        )
        self.assertEquals(
            [],
            html_linter.HTML5Linter(
                '<link href="foo.css">\n' +
                '<link type="foo" href="foo.foo">\n').messages
        )

    def test_style_type(self):
        self.assertEquals(
            [html_linter.ConcernsSeparationMessage(
                line=1, column=1, tag='style'),
             html_linter.TypeAttributeMessage(line=1, column=8, tag='style')],
            html_linter.HTML5Linter('<style type="text/css">').messages
        )

    def test_script_type(self):
        self.assertEquals(
            [html_linter.TypeAttributeMessage(line=1, column=9, tag='script')],
            html_linter.HTML5Linter(
                '<script type="text/javascript" src="foo.js">').messages
        )
        self.assertEquals(
            [],
            html_linter.HTML5Linter(
                '<script src="foo.js">\n' +
                '<script type="foo" src="foo.foo">\n').messages
        )

    def test_script_with_content(self):
        self.assertEquals(
            [html_linter.ConcernsSeparationMessage(
                line=1, column=1, tag='script')],
            html_linter.HTML5Linter('<script></script>').messages
        )
        self.assertEquals(
            [],
            html_linter.HTML5Linter('<script src="foo.js"></script>').messages
        )

    def test_inline_script_with_charset(self):
        self.assertEquals(
            [html_linter.ConcernsSeparationMessage(
                line=1, column=1, tag='script'),
             html_linter.InvalidAttributeMessage(
                line=1, column=9, attribute='charset')],
            html_linter.HTML5Linter(
                '<script charset="utf-8"></script>').messages
        )
        self.assertEquals(
            [],
            html_linter.HTML5Linter(
                '<script src="foo.js" charset="utf-8"></script>').messages
        )

    def test_script_with_obsolete_language(self):
        self.assertEquals(
            [html_linter.ConcernsSeparationMessage(
                line=1, column=1, tag='script'),
             html_linter.InvalidAttributeMessage(
                line=1, column=9, attribute='language')],
            html_linter.HTML5Linter(
                '<script language="foo"></script>').messages
        )
        self.assertEquals(
            [html_linter.InvalidAttributeMessage(
                line=1, column=22, attribute='language')],
            html_linter.HTML5Linter(
                '<script src="foo.js" language="utf-8"></script>').messages
        )

    def test_style_tag(self):
        self.assertEquals(
            [html_linter.ConcernsSeparationMessage(
                line=1, column=1, tag='style')],
            html_linter.HTML5Linter('<style></style>').messages
        )

    def test_style_attribute(self):
        self.assertEquals(
            [html_linter.ConcernsSeparationMessage(
                line=1, column=4, tag='a', attribute='style')],
            html_linter.HTML5Linter('<a style="color:red">a</a>').messages
        )

    def test_a_tag_with_javascript(self):
        self.assertEquals(
            [html_linter.ConcernsSeparationMessage(
                line=1, column=10, tag='a', attribute='href')],
            html_linter.HTML5Linter('<a href="javascript:foo();">').messages
        )
        self.assertEquals(
            [],
            html_linter.HTML5Linter('<a href="foo">').messages
        )

    def test_a_tag_with_void_zero(self):
        self.assertEquals(
            [html_linter.VoidZeroMessage(line=1, column=10),
             html_linter.VoidZeroMessage(line=2, column=10),
             html_linter.VoidZeroMessage(line=3, column=10)],
            html_linter.HTML5Linter(
                '<a href="javascript:void(0);">\n' +
                '<a href="javascript: void(0);">\n' +
                '<a href="javascript: void(0)">').messages
        )

    def test_a_tag_with_name_attribute(self):
        self.assertEquals(
            [html_linter.InvalidAttributeMessage(
                line=1, column=4, attribute='name')],
            html_linter.HTML5Linter('<a name="foo">').messages
        )

    def test_tag_with_event_handler(self):
        self.assertEquals(
            [html_linter.ConcernsSeparationMessage(
                line=1, column=7, tag='body', attribute='onload')],
            html_linter.HTML5Linter('<body onload="foo();">').messages
        )

    def test_tag_with_event_handler_and_js_protocol(self):
        self.assertEquals(
            [html_linter.ConcernsSeparationMessage(
                line=1, column=7, tag='body', attribute='onload'),
             html_linter.InvalidHandlerMessage(
                line=1, column=15, attribute='onload')],
            html_linter.HTML5Linter(
                '<body onload="javascript:foo();">').messages
        )

    def test_urls_have_protocol(self):
        self.assertEquals(
            [html_linter.ProtocolMessage(line=1, column=10, protocol='http:'),
             html_linter.ProtocolMessage(
                line=2, column=11, protocol='https:')],
            html_linter.HTML5Linter(
                '<a href="http://foo.com">\n' +
                '<img src="https://foo.com">').messages
        )
        self.assertEquals(
            [],
            html_linter.HTML5Linter(
                '<a href="//foo.com">\n<img src="//foo.com">').messages
        )

    def test_names(self):
        self.assertEquals(
            [html_linter.NameMessage(
                line=1, column=10, attribute='id', value='a_b'),
             html_linter.NameMessage(
                line=2, column=13, attribute='class', value='Foo'),
             html_linter.NameMessage(
                line=3, column=13, attribute='class', value='a_b'),
             html_linter.NameMessage(
                line=3, column=22, attribute='id', value='Foo')],
            html_linter.HTML5Linter(
                '<div id="a_b">\n' +
                '<img class="Foo">\n' +
                '<div class="a_b" id="Foo">').messages
        )
        self.assertEquals(
            [],
            html_linter.HTML5Linter(
                '<div id="a-b">\n<img class="foo">').messages
        )

    def test_case(self):
        self.assertEquals(
            [html_linter.CapitalizationMessage(line=1, column=2, tag='A'),
             html_linter.CapitalizationMessage(
                line=1, column=4, tag='A', attribute='HREF'),
             html_linter.CapitalizationMessage(
                line=1, column=17, tag='A', closing=True),
             html_linter.CapitalizationMessage(
                line=2, column=4, tag='A', attribute='itemScope')],
            html_linter.HTML5Linter(
                '<A HREF="">foo</A>\n<a itemScope>').messages
        )

    def test_case_with_numeric_attribute(self):
        # Tests https://github.com/deezer/html-linter/issues/3, because of
        # python bug http://bugs.python.org/issue13822.
        self.assertEquals(
            [],
            html_linter.HTML5Linter(
                '<a href="" 0>foo</a>').messages
        )

    def test_quotation(self):
        self.assertEquals(
            [html_linter.QuotationMessage(line=1, column=9, quotation="'"),
             html_linter.QuotationMessage(line=1, column=22, quotation='')],
            html_linter.HTML5Linter('<a href=\'foo\' target=_blank>').messages
        )

    def test_indentation(self):
        self.assertEquals(
            [html_linter.IndentationMessage(
                line=2, column=1, indent=3, max_indent=2)],
            html_linter.HTML5Linter('<div>\n   <a>').messages
        )
        # If we indented by something that is not a multiple of two, we
        # normalize it to a multiple of two so to minimize subsequent
        # false positives.
        self.assertEquals(
            [html_linter.IndentationMessage(
                line=2, column=1, indent=1, max_indent=2)],
            html_linter.HTML5Linter('<div>\n <a>\n</div>').messages
        )
        self.assertEquals(
            [html_linter.IndentationMessage(
                line=2, column=1, indent=1, max_indent=4)],
            html_linter.HTML5Linter('  <a></a>\n </div>\n<div>').messages
        )
        # If we indented by something greater than the maximum allowed we
        # normalize it to the previous maximum.
        self.assertEquals(
            [html_linter.IndentationMessage(
                line=2, column=1, indent=3, max_indent=2)],
            html_linter.HTML5Linter('<a></a>\n   </div>\n    <div>').messages
        )
        # This case should raise two warnings, because the first indentation is
        # normalized to 2 spaces and the second is 6 spaces.
        self.assertEquals(
            [html_linter.IndentationMessage(
                line=2, column=1, indent=3, max_indent=2),
             html_linter.IndentationMessage(
                line=3, column=1, indent=6, max_indent=4)],
            html_linter.HTML5Linter('<a></a>\n   </div>\n      <div>').messages
        )

        self.assertEquals(
            [],
            html_linter.HTML5Linter('<div>\n  <a>').messages
        )
        # Tabs are replaced by two spaces, so we are only getting the Tab error.
        self.assertEquals(
            [html_linter.TabMessage(line=2, column=1)],
            html_linter.HTML5Linter('<div>\n\t<a>').messages
        )

    def test_spaces_between_tags(self):
        self.assertEquals(
            [],
            html_linter.HTML5Linter('<div> <a>   <img>').messages
        )

    def test_formatting(self):
        self.assertEquals(
            [html_linter.FormattingMessage(line=1, column=5, tag='li'),
             html_linter.FormattingMessage(line=1, column=9, tag='div'),
             html_linter.FormattingMessage(line=1, column=14, tag='table'),
             html_linter.FormattingMessage(line=1, column=21, tag='tr'),
             html_linter.FormattingMessage(line=1, column=25, tag='td')],
            html_linter.HTML5Linter('<ul><li><div><table><tr><td>').messages
        )

    def test_boolean_attribute(self):
        self.assertEquals(
            [html_linter.BooleanAttributeMessage(
                line=1, column=21, attribute='checked', value='checked'),
             html_linter.BooleanAttributeMessage(
                line=2, column=8, attribute='autoplay', value='')],
            html_linter.HTML5Linter(
                '<input type="radio" checked="checked">\n' +
                '<video autoplay="">').messages
        )
        self.assertEquals(
            [],
            html_linter.HTML5Linter(
                '<input type="radio" checked>\n<video autoplay>').messages
        )

    def test_http_equiv(self):
        self.assertEquals(
            [html_linter.HTTPEquivMessage(
                line=2, column=7, http_equiv='content-type'),
             html_linter.HTTPEquivMessage(
                line=3, column=7, http_equiv='content-language'),
             html_linter.HTTPEquivMessage(
                line=4, column=7, http_equiv='pragma'),
             html_linter.HTTPEquivMessage(
                line=5, column=7, http_equiv='expires'),
             html_linter.HTTPEquivMessage(
                line=6, column=7, http_equiv='set-cookie'),
             html_linter.HTTPEquivMessage(line=7, column=7, http_equiv='foo')],
            html_linter.HTML5Linter(
                '<meta charset="utf-8">\n' +
                '<meta http-equiv="content-type">\n' +
                '<meta http-equiv="content-language">\n' +
                '<meta http-equiv="pragma">\n' +
                '<meta http-equiv="expires">\n' +
                '<meta http-equiv="set-cookie">\n' +
                '<meta http-equiv="foo">').messages
        )
        self.assertEquals(
            [],
            html_linter.HTML5Linter(
                '<meta charset="utf-8">\n' +
                '<meta http-equiv="refresh">\n' +
                '<meta http-equiv="default-style">\n' +
                '<meta http-equiv="x-ua-compatible">').messages
        )

    def test_whitespaces(self):
        self.assertEquals(
            [html_linter.ExtraWhitespaceMessage(line=1, column=4),
             html_linter.ExtraWhitespaceMessage(line=1, column=10),
             html_linter.ExtraWhitespaceMessage(line=1, column=12),
             html_linter.ExtraWhitespaceMessage(line=1, column=18),
             html_linter.ExtraWhitespaceMessage(line=1, column=25),
             html_linter.ExtraWhitespaceMessage(line=1, column=27),
             html_linter.VoidElementMessage(
                line=1, column=32, tag='br', trailing_chars=' /')],
            html_linter.HTML5Linter(
                '<a   href = "foo" >Foo</ a ><br />').messages
        )
        # The br only raises a VoidElementMessage and not an
        # ExtraWhitespaceMessage because we want to reduce the number of
        # messages and the VoidElementMessage alreadys asks to remove the
        # whitespace.
        self.assertEquals(
            [],
            html_linter.HTML5Linter('<a href="foo">Foo</a>').messages
        )

    def test_multiline_tag_whitespaces(self):
        self.assertEquals(
            [],
            html_linter.HTML5Linter(
                '<a href="foo"\n  target="_blank">Foo</a>').messages
        )


class TestHTML5LinterFunction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.invalid_html = io.open(os.path.join(os.path.dirname(__file__),
                                                'data',
                                                'invalid.html')).read()
        cls.valid_html = io.open(os.path.join(os.path.dirname(__file__),
                                              'data',
                                              'valid.html')).read()

    def test_invalid(self):
        self.assertEquals(
            49, len(html_linter.lint(self.invalid_html).split('\n')))
        self.assertEquals(
            48,
            len(html_linter.lint(
                self.invalid_html,
                exclude=[html_linter.HTTPEquivMessage]).split('\n')))
        self.assertEquals(
            43,
            len(html_linter.lint(
                self.invalid_html,
                exclude=[html_linter.HTTPEquivMessage,
                         html_linter.OptionalTagMessage]).split('\n')))

    def test_valid(self):
        self.assertEquals('', html_linter.lint(self.valid_html))


class TestHTML5LinterUtils(unittest.TestCase):
    @staticmethod
    def get_linter(last_data, last_data_position):
        """Returns a linter instance with the last_data set."""
        linter = html_linter.HTML5Linter('')
        linter._last_data = last_data
        linter._last_data_position = last_data_position

        return linter

    def test_get_indentation(self):
        self.assertEquals(
            None, self.get_linter(' ', (1, 0))._get_indentation())
        self.assertEquals(
            None, self.get_linter(' ', (1, 2))._get_indentation())
        self.assertEquals(
            None, self.get_linter(' a', (1, 1))._get_indentation())
        self.assertEquals(
            1, self.get_linter(' ', (1, 1))._get_indentation())
        self.assertEquals(
            2, self.get_linter('  ', (1, 1))._get_indentation())
        self.assertEquals(
            2, self.get_linter('\t', (1, 1))._get_indentation())
        self.assertEquals(
            4, self.get_linter('\t\t', (1, 1))._get_indentation())
        self.assertEquals(
            5, self.get_linter('\t \t', (1, 1))._get_indentation())
        self.assertEquals(
            3, self.get_linter(' \n \n   ', (1, 2))._get_indentation())
        self.assertEquals(
            None, self.get_linter(' \n \n   a', (1, 2))._get_indentation())

    def test_get_line_column(self):
        self.assertEquals((2, 10),
                          html_linter.get_line_column('foo', 2, 8, 2))
        self.assertEquals((3, 3),
                          html_linter.get_line_column('foo\nbar', 2, 8, 6))
        self.assertEquals((3, 3),
                          html_linter.get_line_column('foo\nbar\n', 2, 8, 6))
        self.assertEquals((3, 4),
                          html_linter.get_line_column('foo\nbar\n', 2, 8, 7))
        self.assertEquals((4, 1),
                          html_linter.get_line_column('foo\nbar\n', 2, 8, 8))

    def test_get_attribute_line_column(self):
        self.assertEquals(
            (2, 11),
            html_linter.get_attribute_line_column(
                '<a href="foo">', 2, 8, 'href'))

        self.assertEquals(
            (3, 3),
            html_linter.get_attribute_line_column(
                '<a href="foo"\n  target="_blank">', 2, 8, 'target'))

        self.assertEquals(
            (3, 19),
            html_linter.get_attribute_line_column(
                '<a href="foo"\n  target="_blank" itemprop>', 2, 8, 'itemprop'))

        self.assertEquals(
            (3, 2),
            html_linter.get_attribute_line_column(
                '<a href=" itemprop "\n itemprop>', 2, 8, 'itemprop'))

        with self.assertRaises(AssertionError):
            html_linter.get_attribute_line_column(
                '<a href=" itemprop "\n itemprop>', 2, 8, 'target')

    def test_get_value_line_column(self):
        self.assertEquals(
            (2, 17),
            html_linter.get_value_line_column(
                '<a href="foo">', 2, 8, 'href'))

        self.assertEquals(
            (2, 17),
            html_linter.get_value_line_column(
                '<a href=\'foo\'>', 2, 8, 'href'))

        self.assertEquals(
            (2, 16),
            html_linter.get_value_line_column(
                '<a href=foo>', 2, 8, 'href'))

        self.assertEquals(
            (2, 18),
            html_linter.get_value_line_column(
                '<a href= "foo">', 2, 8, 'href'))

        self.assertEquals(
            (3, 11),
            html_linter.get_value_line_column(
                '<a href="foo"\n  target="_blank">', 2, 8, 'target'))

        self.assertEquals(
            (3, 27),
            html_linter.get_value_line_column(
                '<a href="foo"\n  target="_blank" itemprop>', 2, 8, 'itemprop'))

        self.assertEquals(
            (3, 10),
            html_linter.get_value_line_column(
                '<a href=" itemprop "\n itemprop>', 2, 8, 'itemprop'))

        with self.assertRaises(AssertionError):
            html_linter.get_value_line_column(
                '<a href=" itemprop "\n itemprop>', 2, 8, 'target')
