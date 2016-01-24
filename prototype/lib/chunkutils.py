from . import ast
from .textutils import splitlines

import sys


def tangle(chunk, meta_data):
    def tangle_elements(elements_src, meta_data):
        yaweb = meta_data['yaweb']
        elements = yaweb.merge_text_elements(elements_src)

        i = 0
        while i < len(elements):
            element = elements[i]
            if ast.is_element_type(element, ast.Use):
                chunk_name = element.get('chunk_name')
                if 'chunks_by_name' in meta_data and chunk_name in meta_data['chunks_by_name']:
                    used_chunks = meta_data['chunks_by_name'][chunk_name]
                    used_elements = [e for ch in used_chunks for e in list(ch)]
                    elements[i:i + 1] = [ast.clone(e) for e in used_elements]
                    i += len(used_elements)
                    if elements[i].text.endswith('\n'):
                        elements[i].text = elements[i].text[0:-1]
            i = i + 1

        if any([ast.is_element_type(e, ast.Use) for e in elements]):
            return tangle_elements(elements)
        else:
            return elements

    tangled_elements = tangle_elements(list(chunk), meta_data)
    result = ''.join([e.text for e in tangled_elements])
    return result


def merge_text_elements(elements):
    result = []

    for element in elements:
        if ast.is_element_type(element, ast.Text):
            if result and ast.is_element_type(result[-1], ast.Text):
                result[-1].text += element.text
            else:
                result.append(ast.Text(text=str(element.text)))
        else:
            result.append(element)

    return result
