print("LENGTH UNITS: km: kilometer, m: meter, cm: centimeter, ft: foot, in: inch")
print("TEMPRATURE UNITS: f: fahrenheit, c: celsius, k: kelvin")
print("WEIGHT UNITS: t:tonnne kg: kilogram, g: gram lb: pounds, oz: ounces")
print()
first_input = input("Enter value with unit (e.g. 10kg): ")
second_input = input("Enter the unit to convert to as given above: ")
second_input = second_input.lower()
#Identify units using dictionary method
length_units = {
    "m": 1,
    "km": 1000,
    "cm": 0.01,
    "ft": 0.3048,
    "in": 0.0254
}
temprature_units = {
    "c": 1,
    "f": -17.2222,
    "k": 273.15
}
weight_units = {
    "kg": 1,
    "t": 1000,
    "g": 0.001,
    "lb": 0.453592,
    "oz": 0.0283495
}
unit_categories = {
     "length": length_units,
     "temp": temprature_units,
     "weight": weight_units
}
#Detects the unit inserted by user
def detect_category(unit):
    for category, units in unit_categories.items():
        if unit in units:
            return category
    return None

def conversion(value, from_unit, to_unit):
    category = detect_category(from_unit)
    if category != detect_category(to_unit):
        return "Units are from different categories"
    
    if category == "length" or category == "weight":
        units = unit_categories[category]
        value_in_base = value * units[from_unit]
        result = value_in_base / units[to_unit]
        return result
    elif category == "temp":
        return temp_conversion(value, from_unit, to_unit)
    else:
        return "Unsupported unit."
    
def temp_conversion(value, from_unit, to_unit):

    if from_unit == "f":
        value = (value - 32) * 5/9
    elif from_unit == "k":
        value = value - temprature_units["k"]

    if to_unit == "f":
         return value * 9/5 + 32
    elif to_unit == "k":
        return value + 273.15
    elif to_unit == "c":
        return value 
    else:
        return "Invalid unit"

#Detects both types of input inserted in the first input (value then string/unit)
def string_type():
    #imports regular expression
    import re
    #Checks for inserted input type and separates it based on two groups: value and unit. The r in the beginning is for the code to detect backlashes. The + after each group is te make any number of digits possible (eg. 50, kg). The *\.? is to allow decimal numbers
    match = re.match(r"([0-9]*\.?[0-9]+)([a-zA-Z]+)", first_input)
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        unit = unit.lower()
        return detect_category(unit), conversion(value, unit, second_input)
    else:
        print("Invalid input")

print(string_type())