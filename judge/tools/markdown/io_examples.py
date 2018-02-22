"""
Definition of a markdown semantic for input-output examples.

An example must be formated with lines starting with '>>' to define inputs and
  then lines starting with '<<' to defines outputs.
For example:
  >> print('42\n42\n')
  >> 42
  >>
  >> 42
  >>
"""
import regex

from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree, AtomicString


class IOEXampleProcessor(BlockProcessor):
    """
    Identify and format example blocks.
    """

    re_input = r'(?:(?:^|\n)[ ]*>>[ ]?(.*))+'
    re_output = r'(?:(?:^|\n)[ ]*<<[ ]?(.*))+'
    re_example = regex.compile(re_input + re_output)

    def test(self, parent, block):
        return bool(self.re_example.match(block))

    def run(self, parent, blocks):
        block = blocks.pop(0)

        # Recover text
        match = self.re_example.match(block)
        input_lines = match.captures(1)
        output_lines = match.captures(2)

        input_text = '\n'.join(input_lines)
        output_text = '\n'.join(output_lines)

        # Create subtree
        main_block = etree.SubElement(parent, 'div')
        in_block = etree.SubElement(main_block, 'pre')
        out_block = etree.SubElement(main_block, 'pre')

        main_block.set('class', 'example')
        in_block.set('class', 'input')
        out_block.set('class', 'output')

        in_block.text = AtomicString(input_text)
        out_block.text = AtomicString(output_text)



class IOExamples(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.parser.blockprocessors.add(
            'io_examples_processor',
            IOEXampleProcessor(md.parser),
            '<quote'
        )
