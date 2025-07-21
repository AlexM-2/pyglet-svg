from pyglet.window import Window
from pyglet.graphics import Batch
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.math import Vec2
from pyglet.text import Label

from lxml import etree

NS = {"svg": "http://www.w3.org/2000/svg"}
STR_NS = "{http://www.w3.org/2000/svg}"

vertex_source = """#version 330 core
    in vec3 position;
    in vec4 colors;
    in vec3 tex_coords;
    in vec3 translation;
    in vec3 view_translation;
    in vec2 anchor;
    in float rotation;
    in float visible;
    in float use_texture;

    out vec4 text_colors;
    out vec2 texture_coords;
    out vec4 vert_position;
    out float using_texture;

    uniform WindowBlock
    {
        mat4 projection;
        mat4 view;
    } window;

    uniform mat4 transform;

    void main()
    {
        mat4 m_rotation = mat4(1.0);
        vec3 v_anchor = vec3(anchor.x, anchor.y, 0);
        mat4 m_anchor = mat4(1.0);
        mat4 m_translate = mat4(1.0);

        m_translate[3][0] = translation.x;
        m_translate[3][1] = translation.y;
        m_translate[3][2] = translation.z;

        m_rotation[0][0] =  cos(-radians(rotation));
        m_rotation[0][1] =  sin(-radians(rotation));
        m_rotation[1][0] = -sin(-radians(rotation));
        m_rotation[1][1] =  cos(-radians(rotation));

        gl_Position = transform * window.projection * window.view * m_translate * m_anchor * m_rotation * vec4(position + view_translation + v_anchor, 1.0) * visible;

        vert_position = vec4(position + translation + view_translation + v_anchor, 1.0);
        text_colors = colors;
        texture_coords = tex_coords.xy;

        using_texture = use_texture;
    }
"""

fragment_source = """#version 330 core
    in vec4 text_colors;
    in vec2 texture_coords;
    in vec4 vert_position;
    in float using_texture;

    out vec4 final_colors;

    uniform sampler2D text;
    uniform bool scissor;
    uniform vec4 scissor_area;

    void main()
    {
        if (using_texture == 3.0) {
            final_colors = text_colors;
        }
        else {
            final_colors = texture(text, texture_coords) * text_colors;
        }
        if (scissor == true) {
            if (vert_position.x < scissor_area[0]) discard;                     // left
            if (vert_position.y < scissor_area[1]) discard;                     // bottom
            if (vert_position.x > scissor_area[0] + scissor_area[2]) discard;   // right
            if (vert_position.y > scissor_area[1] + scissor_area[3]) discard;   // top
        }
    }
"""

text_vertex_shader = Shader(vertex_source, "vertex")
text_fragment_shader = Shader(fragment_source, "fragment")
text_program = ShaderProgram(text_vertex_shader, text_fragment_shader)

#helper function used in extracting data from 'transform' attributes in svg elements
def get_transformation(elem, group_elem):
    def extract_transformation(data):
        return data[0], Vec2(data[1].split(","))
    
    transform_attr = elem.get("transform") or group_elem.get("transform") or ""
    return [extract_transformation(transform.split("(")) for transform in transform_attr.split(")")[:-1]]

def get_style(elem):
    return {string.split(":")[0]: string.split(":")[1] for string in elem.get("style").split(";")}

class Value:

    UNITS = {"px", "in"}
    NUMERICAL_SET = {"0", "1", "2", "3", "4", "5", "6", "7", "9", "."}
    NUMERICAL_DICT = {value: "" for value in NUMERICAL_SET}

    def __init__(self, value: str):
        self.str_data = value #the source data in a string format, eg: str("19.6653px")
    
    def get_data_and_unit(self) -> tuple[float, str]:

        str_data = self.str_data
        data_unit_stripped_: str = str_data
        out_unit: str | None = None #initialize unit as None

        for unit in self.UNITS: #loop through all the units supported by this SVG loader/parser/renderer

            data_unit_stripped_ = data_unit_stripped_.replace(unit, "") #get the data with the current unit stripped

            #if the unit used by the data is the same as the current unit in the loop
            if not data_unit_stripped == str_data: 
                out_unit = unit #set the return unit to the current unit in the loop
        
        #if it is using user units (out_unit has not changed having been through the above for loop and is still 
        # None (what it was initialised as))
        if out_unit == None:
            out_unit = "px" #default to pixels
        
        return float(data_unit_stripped), out_unit

    @property
    def data(self):

        global data_unit_stripped
        data_unit_stripped = self.str_data

        for unit in self.UNITS: #loop through all the units supported by this SVG loader/parser/renderer
            data_unit_stripped = data_unit_stripped.replace(unit, "") #get the data with the current unit stripped
        
        return float(data_unit_stripped)
    
    @property
    def unit(self):
        trans_table = self.str_data.maketrans(self.NUMERICAL_DICT)
        return self.str_data.translate(trans_table)


    def in_pixels(self): #TODO
        n_data, unit = self.get_data_and_unit()

        match unit:
            case "px":
                return n_data
            case "in":
                return self.in_to_px(n_data)
    
    def in_to_px(self, inches: float | int):
        return inches * 96

def has_text(element):
    if element.text == "":
        return False
    else:
        return True

class SVGFile:
    def __init__(self, file_path_or_tree: str | etree._ElementTree):
        if type(file_path_or_tree) == str:
            self.tree: etree._ElementTree = etree.parse(file_path_or_tree)
        elif type(file_path_or_tree) == etree._ElementTree:
            self.tree = file_path_or_tree
        else:
            raise TypeError("'file_path_or_tree' must be a file path (str) to a valid svg document or an lxml.etree._ElementTree object containing valid svg data")

        self.batch = Batch()

        groups = []
        for group_elem in self.tree.xpath("//svg:g", namespaces= NS):
            out_group: list = []

            for elem in group_elem.xpath(".//svg:*", namespaces= NS):
                if elem.tag == STR_NS + "text":
                    
                    transformations = get_transformation(elem, group_elem)

                    tspans = []
                    tspan_elems = elem.xpath("./svg:tspan", namespaces=NS)
                    if len(tspan_elems) < 1 and not has_text(elem):
                        pass
                    for tspan_elem in tspan_elems:
                        
                        style = get_style(tspan_elem)
                        # tspans.append(Label(
                        #     text=tspan_elem.text,
                        #     x=float(tspan_elem.get("x")),
                        #     y=float(tspan_elem.get("y")),
                        #     multiline=False,
                        #     font_name=style["font-family"],
                        #     font_size=Value(style["font-size"]).in_pixels(),
                        #     weight=style["font-weight"],
                        #     italic=style["font-style"] == "italic",
                        #     stretch=False,
                        #     color=style["fill"],
                        #     batch=self.batch,
                        #     program=text_program
                        # ))
                
                out_group.append(elem)
        
            groups.append(out_group)
        
        self.groups = groups
    
    def draw(self):
        self.batch.draw()

def main():
    window = Window()
    svg = SVGFile("Assets/play-button.svg")

    value = Value("19.6679in")
    print(f"{value.str_data=}\n")
    print(f"{value.data=}\n")
    print(f"{value.unit=}\n")
    print(f"{value.in_pixels()=}\n")

if __name__ == "__main__":
    main()