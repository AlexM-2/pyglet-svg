from string import printable

UNITS = [
    "px", "in", "cm", "mm", "pt", "pc", "q", #absolute units
    "em", "ex", "ch", "rem", "lh", "%", "vw", "vh", "vmin", "vmax" #relative units
]

#the charcters that need to be removed from the source string data to leave only the unit
NUMERICAL = "0123456789."
#a dict that can be used in str.maketrans() to make a translation table that can be used in str.translate() to
# remove all numerical characters from the source string data to leave only the unit
NUMERICAL_DICT = {value: "" for value in NUMERICAL}

NON_NUMERICAL = printable.translate(printable.maketrans(NUMERICAL_DICT))
NON_NUMERICAL_DICT = {value: "" for value in NON_NUMERICAL}

PX_PER_IN = 96
CM_PER_IN = 2.54
MM_PER_IN = 25.4
PT_PER_IN = 72
PC_PER_IN = 6
Q_PER_IN = 101.6

class Value:
    def __init__(self, data: float | int, unit: str, **context):

        if not data == float() | int():
            raise TypeError(f"Value() argument 'data' must be a float or integer, not {type(data)}")
        if not unit == str():
            raise TypeError(f"Value() argument 'unit' must be a str, not {type(unit)}")
        if not unit in UNITS:
            raise ValueError(f"Value() argument 'unit' must a valid unit supported by pylget-svg, not {unit}")
        
        self._data = data
        self._unit = unit
        self._str_data = str(data) + str(unit)
        self._dirty = False

        self.context = context
    
    def __str__(self):
        return self.str_data
    
    @property
    def str_data(self):
        if self._dirty == True:
            self._str_data = str(self._data) + str(self._unit)
        
        return self._str_data
    
    @property
    def unit(self):
        return self._unit
    
    @unit.setter
    def unit(self, unit: str):
        if not unit == str():
            raise TypeError(f"Value.unit must be a str, not {type(unit)}")
        if not unit in UNITS:
            raise ValueError(f"Value.unit must a valid unit supported by pylget-svg, not {unit}")
        
        self._dirty = True
        self._unit = unit
    
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, data: float | int):
        if not data == float() | int():
            raise TypeError(f"Value.data must be a float or integer, not {type(data)}")
        
        self._dirty = True
        self._data = data
    
    def convert(self, unit: str, **context):
        self.unit = unit

        self._data = convert(self._data, self._unit, unit, **(context or self.context))

def get_data(str_data: str):
    return str_data.translate(str_data.maketrans(NON_NUMERICAL_DICT))

def get_unit(str_data: str):
    return str_data.translate(str_data.maketrans(NUMERICAL_DICT))

def get_data_and_unit_str(str_data: str):
    return get_data(str_data), get_unit(str_data)

def get_data_and_unit(str_data: str):
    return float(get_data(str_data)), get_unit(str_data)

def get_px(value: float, from_unit: str, **context) -> float:
    fs = context.get("font_size", 16)
    rfs = context.get("root_font_size", fs)
    xh = context.get("x_height_ratio", 0.5)
    zw = context.get("zero_width_ratio", 0.5)
    lh = context.get("line_height", fs)
    ref = context.get("reference_length", 100)
    vw = context.get("viewport_width", 100)
    vh = context.get("viewport_height", 100)
    vmin = context.get("vmin", min(vw, vh))
    vmax = context.get("vmax", max(vw, vh))

    if from_unit == "px": return value
    if from_unit == "in": return value * PX_PER_IN
    if from_unit == "cm": return value * (PX_PER_IN / CM_PER_IN)
    if from_unit == "mm": return value * (PX_PER_IN / MM_PER_IN)
    if from_unit == "pt": return value * (PX_PER_IN / PT_PER_IN)
    if from_unit == "pc": return value * (PX_PER_IN / (PT_PER_IN / 12))
    if from_unit == "q": return value * (PX_PER_IN / Q_PER_IN)
    if from_unit == "em": return value * fs
    if from_unit == "ex": return value * fs * xh
    if from_unit == "ch": return value * fs * zw
    if from_unit == "rem": return value * rfs
    if from_unit == "lh": return value * lh
    if from_unit == "%": return (value / 100.0) * ref
    if from_unit == "vw": return (value / 100.0) * vw
    if from_unit == "vh": return (value / 100.0) * vh
    if from_unit == "vmin": return (value / 100.0) * vmin
    if from_unit == "vmax": return (value / 100.0) * vmax

    raise ValueError(f"Unsupported unit: {from_unit}")

def from_px(px: float, to_unit: str, **context) -> float:
    fs = context.get("font_size", 16)
    rfs = context.get("root_font_size", fs)
    xh = context.get("x_height_ratio", 0.5)
    zw = context.get("zero_width_ratio", 0.5)
    lh = context.get("line_height", fs)
    ref = context.get("reference_length", 100)
    vw = context.get("viewport_width", 100)
    vh = context.get("viewport_height", 100)
    vmin = context.get("vmin", min(vw, vh))
    vmax = context.get("vmax", max(vw, vh))

    if to_unit == "px": return px
    if to_unit == "in": return px / PX_PER_IN
    if to_unit == "cm": return px / (PX_PER_IN / CM_PER_IN)
    if to_unit == "mm": return px / (PX_PER_IN / MM_PER_IN)
    if to_unit == "pt": return px / (PX_PER_IN / PT_PER_IN)
    if to_unit == "pc": return px / 16  # (12 pt/in × 72 pt = 96 px)
    if to_unit == "q": return px / (PX_PER_IN / Q_PER_IN)
    if to_unit == "em": return px / fs
    if to_unit == "ex": return px / (fs * xh)
    if to_unit == "ch": return px / (fs * zw)
    if to_unit == "rem": return px / rfs
    if to_unit == "lh": return px / lh
    if to_unit == "%": return (px / ref) * 100
    if to_unit == "vw": return (px / vw) * 100
    if to_unit == "vh": return (px / vh) * 100
    if to_unit == "vmin": return (px / vmin) * 100
    if to_unit == "vmax": return (px / vmax) * 100

    raise ValueError(f"Unsupported unit: {to_unit}")

def convert(data: float | int, from_unit: str, to_unit: str, **context):
    if not data == float() | int():
        raise TypeError(f"convert() argument 'data' must be a float or int, not {type(data)}")
    if not from_unit == str():
        raise TypeError(f"convert() argument 'from_unit' must a str, not {type(from_unit)}")
    if not from_unit in UNITS:
        raise ValueError(f"convert() argument 'from_unit' must be a valid unit supported by pyglet-svg, not {from_unit}'")
    if not to_unit == str():
        raise TypeError(f"convert() argument 'to_unit' must a str, not {type(to_unit)}")
    if not to_unit in UNITS:
        raise ValueError(f"convert() argument 'to_unit' must be a valid unit supported by pyglet-svg, not {to_unit}'")

    return from_px(get_px(data, from_unit, to_unit, **context), to_unit, **context)

def convert_str(str_data: str, to_unit: str, **context) -> float:
    """Convert data in the format '<data><unit>' to another unit"""
    data = get_data(str_data)
    unit = get_unit(str_data)

    if not data == float() | int():
        raise TypeError(f"convert_str() argument 'data' must be a float or int, not {type(data)}")
    if not to_unit == str():
        raise TypeError(f"convert_str() argument 'to_unit' must a str, not {type(to_unit)}")
    if not to_unit in UNITS:
        raise ValueError(f"convert_str() argument 'to_unit' must be a valid unit supported by pyglet-svg, not {to_unit}'")
    
    return convert(data, unit, to_unit, **context)

def main() -> None:
    pass

if __name__ == "__main__":
    main()