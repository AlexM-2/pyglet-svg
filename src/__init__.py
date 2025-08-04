from pyglet.graphics import Batch
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.math import Vec2
from pyglet.text.document import UnformattedDocument
from pyglet.text.layout.base import TextLayout

from xml.etree import ElementTree as ET

import units

__all__ = ["units"]

NS = {"svg": "http://www.w3.org/2000/svg"}
STR_NS = "{http://www.w3.org/2000/svg}"

#helper function used in extracting data from 'transform' attributes in svg elements
def get_transformation(elem: ET.Element):
    """Extract transformation data from an SVG element's 'transform' attribute Eg:
    "translate(50,100)scale(1.5,2)"""
    def extract_transformation(data: list[str]):
        return data[0], Vec2(units.Value(number).in_pixels() for number in data[1].split(","))
    
    transform_attr = elem.get("transform")
    return [extract_transformation(transform.split("(")) for transform in transform_attr.split(")")[:-1]]

def get_style(elem: ET.Element):
    """Extract CSS data from an SVG element's 'style' attribute and return a dict containing the data. Eg:
    
    "fill:#000000;fill-opacity:0;stroke:#7dffff" -> {"fill":"#000000", "fill-opacity":"0", "stroke":"#7dffff"}"""
    return {string.split(":")[0]: string.split(":")[1] for string in elem.get("style").split(";")}

def get_path(elem: ET.Element):
    path_attr = elem.get("d")

def has_text(element):
    if element.text == "":
        return False
    else:
        return True

class SVGFile:
    def __init__(self, file_path_or_tree: str | ET.ElementTree):

        if file_path_or_tree.__class__ == str:
            self.tree: ET.ElementTree = ET.parse(file_path_or_tree)
        elif file_path_or_tree.__class__ == ET.ElementTree:
            self.tree = file_path_or_tree
        else:
            raise TypeError("'file_path_or_tree' must be a file path (str) to a valid svg document or an lxml.etree._ElementTree object containing valid svg data")

        self.batch = Batch()

        root = self.tree.getroot()

        def loop(root: ET.Element):
            for elem in root.findall("./*"):
                print(elem.tag)
                if elem.tag == STR_NS+"g":
                    loop(elem)
                elif elem.tag == STR_NS+"text":
                    doc = UnformattedDocument(elem.text)
                    doc.set_style(0, 1, {""})

        loop(root)

    def draw(self):
        self.batch.draw()

def main():
    svg = SVGFile("test_svgs/drawing-1.svg")

if __name__ == "__main__":
    main()