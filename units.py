from typing import Self, overload

UNITS = {"px", "in"} #all the units supported by pyglet-svg

#the charcters that need to be removed from the source string data to leave only the unit
NUMERICAL_SET = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."}
#a dict that can be used in str.maketrans() to make a translation table that can be used in str.translate() to
# remove all numerical characters from the source string data to leave only the unit
NUMERICAL_DICT = {value: "" for value in NUMERICAL_SET}

class Value:

    @overload
    def __init__(self, str_data: str): ...
    @overload
    def __init__(self, value: Self): ...
    @overload
    def __init__(self, data: float, unit: str): ...
    def __init__(self, arg1, arg2 = None):
        
        match (arg1, arg2):
            case (str(), None):
                self.str_data = arg1
            case (Value(), None):
                self.str_data = arg1.str_data
            case (float(), str()):
                self.str_data = str(arg1) + arg2
            case (_, _):
                raise TypeError("Invalid types for 'arg1' and/or 'arg2'")

    
    def __str__(self):
        return self.str_data
    
    def get_data_and_unit(self) -> tuple[str, str]:
        return get_data_and_unit(self.str_data)
    
    def get_data_str(self):
        return get_data_str(self.str_data)

    @property
    def data(self):
        return get_data(self.str_data)
        
    
    @data.setter
    def data(self, number: float | str):
        self.str_data = str(number) + self.unit

    @property
    def unit(self):
        return get_unit(self.str_data)
    
    @unit.setter
    def unit(self, unit: str, modify_data: bool = True):
        if modify_data == False:
            self.str_data = self.get_data_str() + unit
        else:
            self.str_data = convert(self, unit).str_data

def get_data_and_unit(str_data) -> tuple[str, str]:

    data_unit_stripped: str = str_data
    out_unit: str | None = None #initialize unit as None

    for unit in UNITS: #loop through all the units supported by this SVG loader/parser/renderer

        data_unit_stripped = data_unit_stripped.replace(unit, "") #get the data with the current unit stripped

        #if the unit used by the data is the same as the current unit in the loop
        if not data_unit_stripped == str_data: 
            out_unit = unit #set the return unit to the current unit in the loop
        
    #if it is using user units (out_unit has not changed having been through the above for loop and is still 
    # None (what it was initialised as))
    if out_unit == None:
        out_unit = "px" #default to pixels
        
    return data_unit_stripped, out_unit

def get_data_str(str_data: str) -> str:

    for unit in UNITS: #loop through all the units supported by this SVG loader/parser/renderer
        str_data = str_data.replace(unit, "") #get the data with the current unit stripped
        
    return str_data

def get_data(str_data: str) -> float:
    return float(get_data_str(str_data))

def get_unit(str_data: str) -> str:
    trans_table = str_data.maketrans(NUMERICAL_DICT)
    return str_data.translate(trans_table)

#defines conversion constants to convert between from every unit to all the other units
CONVERSION_TABLE = {
    "px": {"px":1,        "in":1/96,    "cm":1/(96/2.54), "mm":1/(96/72), "pt":1/(96/72), "pc":1/16,    "q":1/(96/101.6)},
    "in": {"px":96,       "in":1,       "cm":2.54,        "mm":25.4,      "pt":72,        "pc":6,       "q":101.6       },
    "cm": {"px":96/2.54,  "in":1/2.54,  "cm":1,           "mm":10,        "pt":72/2.54,   "pc":6/2.54,  "q":40          },
    "mm": {"px":96/25.4,  "in":1/25.4,  "cm":1/10,        "mm":1,         "pt":72/25.4,   "pc":6/25.4,  "q":4           },
    "pt": {"px":96/72,    "in":1/72,    "cm":2.54/72,     "mm":25.4/72,   "pt":1,         "pc":1/12,    "q":101.6/72    },
    "pc": {"px":16,       "in":1/6,     "cm":2.54/6,      "mm":25.4/6,    "pt":12,        "pc":1,       "q":101.6/6     },
    "q":  {"px":96/101.6, "in":1/101.6, "cm":1/40,        "mm":1/4,       "pt":72/101.6,  "pc":6/101.6, "q":1           },
}

@overload
def convert(str_data: str, unit: str) -> Value: ...
@overload
def convert(data: Value, unit: str) -> Value: ...
def convert(arg1: Value | str, unit: str) -> Value:
    match (arg1, unit):
        case (Value(), str()):
            return Value(arg1.data * CONVERSION_TABLE[arg1.unit][unit], unit)
        case (str(), str()):
            return Value(arg1)



def main() -> None:
    value = Value("200.234px")
    print(value)
    value.unit = "in"
    print(value.data, value.unit)

if __name__ == "__main__":
    main()