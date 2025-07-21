from pyglet.graphics.shader import Shader, ShaderProgram
from lxml import etree

NS = {"svg": "http://www.w3.org/2000/svg"}

vertex_source = """
#version 330

layout(location = 0) in vec2 vertices;
layout(location = 1) in vec4 colors;

out vec4 newColor;

void main()
{
    gl_Position = vec4(vertices, 0.0f, 0.0f);
    newColor = colors;
}
"""

fragment_source = """
#version 330

in vec4 newColor;

out vec4 finalColor;

void main()
{
    finalColor = newColor;
}
"""

class SVGFile:
    def __init__(self, file_path: str):
        self.tree: etree._ElementTree = etree.parse(file_path)

        self.vertex_shader = Shader(vertex_source, "vertex")
        self.fragment_shader = Shader(fragment_source, "fragment")
        self.shader_program = ShaderProgram(self.vertex_shader, self.fragment_shader)

        self.parse()

        # self.shader_program.vertex_list_indexed()
    
    def parse(self):
        groups = []
        print("parsing")
        for group_elem in self.tree.xpath("//svg:g", namespaces= NS):
            out_group: list = []

            for elem in group_elem.xpath(".//svg:*", namespaces= NS):
                print(elem.tag)
                
                out_group.append(elem)
        
            groups.append(out_group)
        

def main():
    svg = SVGFile("Assets/play_button.svg")
    

if __name__ == "__main__":
    main()