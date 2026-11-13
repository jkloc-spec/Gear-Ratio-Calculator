from drafter import *
from dataclasses import dataclass
from bakery import assert_equal
from math import cos, sin, pi
from urllib.parse import quote

set_website_title("Gear Ratio Calculator")
set_site_information(
    author = "Joey Kloc",
    description = "Gear Ratio Calculator for students",
    sources=["My Teachers and my TA's & Claude"],
    planning= ["Design.pdf", "Problem.pdf"]    
    links=["https://github.com/jkloc-spec/Gear-Ratio-Calculator.git"],
)
hide_debug_information()
set_website_framed(False)
min_speed = 0
max_speed = 100000
min_torque = 0
max_torque = 100000
min_teeth = 6
max_teeth = 120
canvas_width = 400
canvas_height = 360
assembly_width = 300

@dataclass
class GearCalculation:
    input_speed: float
    input_torque: float
    input_teeth: int
    output_teeth: int
    gear_ratio: float
    output_speed: float
    output_torque: float

@dataclass
class State:
    input_speed: float
    input_torque: float
    input_teeth: int
    output_teeth: int
    gear_ratio: float
    history: list[GearCalculation]

def is_number(text: str) -> bool:
    """Return true if the number is like 13 or 13.5 no negatives or letters
    Args:
        text (str): The text typed by the user.
    Returns:
        bool: True if text is a number, otherwise False.
    """
    return text.replace(".", "", 1).isdigit()
def gear_ratio(input_teeth: int, output_teeth: int)-> float:
     """Return output teeth divided by input teeth
     Args:
        input_teeth (int): Number of teeth on the input gear.
        output_teeth (int): Number of teeth on the output gear.
     Returns:
        float: The gear ratio."""
     return output_teeth / input_teeth

def output_speed(input_speed: float, ratio: float) -> float:
    """ Returns the output speed in RPM using the formula (input speed / ratio)
    Args:
        input_speed (float): Input speed in RPM
        ratio (float): The gear ratio
    Returns:
        float: The output speed in RPM"""
    return input_speed/ratio

def output_torque(input_torque: float, ratio: float) -> float:    
    """ Returns the output torque in Nm using the formula (input torque * ratio)
    Args:
        input_torque (float): Input torque in Nm
        ratio (float): The gear ratio
    Returns:
        float: The output torque in Nm"""
    return input_torque * ratio

def speed_is_valid(input_speed: str) -> bool:
    """ Returns True if speed is a number above min_speed and within max_speed
    Args:
        input_speed (str): The speed text typed by the user
    Returns:
        bool: True if the speed is valid, otherwise False"""
    return is_number(input_speed) and min_speed < float(input_speed) <= max_speed

def torque_is_valid(input_torque:str) -> bool:
    """Return True if the torque is a number above min_torque and within max_torque
    Args:
        input_torque (str): The torque text typed by the user.
    Returns:
        bool: True if the torque is valid, otherwise False."""
    return is_number(input_torque) and min_torque < float(input_torque) <= max_torque

def teeth_are_valid(teeth: str) -> bool:
    """Return True if the teeth count is a number between min_teeth to max_teeth
    Args:
        teeth (str): The teeth text typed by the user.
    Returns:
        bool: True if the teeth count is valid, otherwise False"""
    return teeth.strip().isdigit() and min_teeth <= int(teeth) <= max_teeth

def describe_ratio(ratio: float) -> str:
    """ Returns a sentence describing what the gear ratio does
     Args:
        ratio (float): The gear ratio
    Returns:
        str: A sentence describing the effect of the ratio"""
    if ratio > 1:
        return "The output gear is slower than the input gear, with more torque."
    if ratio < 1:
        return "The output gear is faster than the input gear, with less torque."
    return "The speed and torque do not change."

def highest_ratio(history: list[GearCalculation]) -> float:
    """Return the largest gear ratio in the history and 0 if it is empty
    Args:
        history (list[GearCalculation]): The saved calculations
    Returns:
        float: The largest gear ratio or 0 if the history is empty"""
    highest = 0.0
    for calculation in history:
        if calculation.gear_ratio > highest:
            highest = calculation.gear_ratio
    return highest

def history_rows(history: list[GearCalculation])->list[list[str]]:
    """Loops over every saved calculation and build one table row for each
    Args:
        history (list[GearCalculation]): The saved calculations.
    Returns:
        list[list[str]]: The table rows """
    HISTORY_TITLES =["Input RPM", "Input Nm", "Input Teeth", "Output Teeth", "Gear Ratio"]
    rows = [list(HISTORY_TITLES)]
    for hist in history:
        row = [
            str(hist.input_speed),
            str(hist.input_torque),
            str(hist.input_teeth),
            str(hist.output_teeth),
            str(hist.gear_ratio),
        ]
        rows.append(row)
    return rows
def gear_points(center_x: float, center_y: float, teeth: int,
                module: float, rotation: float) -> str:
    """Build the outline points of a gear as an SVG polygon string.

    ADVANCED TECHNIQUE (not covered in class): this uses sin and cos from the
    math module to place each point on a circle (x = r*cos(angle),
    y = r*sin(angle)). Each tooth is a four-point trapezoid, so every gear
    has teeth * 4 points. The module is the pixels of pitch diameter per tooth.

    Args:
        center_x (float): The x position of the gear's center.
        center_y (float): The y position of the gear's center.
        teeth (int): The number of teeth on the gear.
        module (float): The pixels of pitch diameter per tooth.
        rotation (float): The angle in radians of the first tooth.
    Returns:
        str: The points as "x,y x,y ..." for an SVG polygon."""
    pitch_radius = module * teeth / 2
    tip_radius = pitch_radius + module
    root_radius = pitch_radius - 1.25 * module
    step = 2 * pi / teeth
    shape = [(-0.25, root_radius), (-0.12, tip_radius),
             (0.12, tip_radius), (0.25, root_radius)]
    points = []
    for tooth in range(teeth):
        tooth_angle = rotation + tooth * step
        for fraction, radius in shape:
            angle = tooth_angle + fraction * step
            x = center_x + radius * cos(angle)
            y = center_y + radius * sin(angle)
            points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)


def spinning_gear(center_x: float, center_y: float, teeth: int, module: float,
                  rotation: float, color: str, direction: int,
                  seconds: float) -> str:
    """Build one spinning, labeled gear as SVG text.

    ADVANCED TECHNIQUE (not covered in class): SVG's animateTransform tag
    makes the gear rotate forever without any extra Python code.

    Args:
        center_x (float): The x position of the gear's center.
        center_y (float): The y position of the gear's center.
        teeth (int): The number of teeth on the gear.
        module (float): The pixels of pitch diameter per tooth.
        rotation (float): The angle in radians of the first tooth.
        color (str): The fill color of the gear.
        direction (int): 1 for clockwise or -1 for counterclockwise.
        seconds (float): The seconds the gear takes to turn once.
    Returns:
        str: The SVG text for the gear."""
    outline = gear_points(center_x, center_y, teeth, module, rotation)
    end_angle = 360 * direction
    center = f"{center_x:.1f} {center_y:.1f}"
    return (
        f'<polygon points="{outline}" fill="{color}" stroke="white">'
        f'<animateTransform attributeName="transform" type="rotate" '
        f'from="0 {center}" to="{end_angle} {center}" '
        f'dur="{seconds:.1f}s" repeatCount="indefinite"/></polygon>'
        f'<circle cx="{center_x:.1f}" cy="{center_y:.1f}" r="6" fill="white"/>'
        f'<text x="{center_x:.1f}" y="{center_y + 24:.1f}" fill="white" '
        f'font-size="16" text-anchor="middle">{teeth}T</text>'
    )


def gear_svg(input_teeth: int, output_teeth: int) -> str:
    """Build an SVG picture of two meshed gears drawn to scale.

    The output gear turns the opposite way, and takes input/output times as
    long per turn as the input gear, which matches the gear ratio.

    Args:
        input_teeth (int): The number of teeth on the input gear.
        output_teeth (int): The number of teeth on the output gear.
    Returns:
        str: The complete SVG text."""
    module = assembly_width / (input_teeth + output_teeth)
    left_x = (canvas_width - assembly_width) / 2 + module * input_teeth / 2
    right_x = left_x + module * (input_teeth + output_teeth) / 2
    center_y = canvas_height / 2
    mesh_rotation = pi + (pi / output_teeth)
    seconds = 4.0
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" '
        f'height="{canvas_height}" viewBox="0 0 {canvas_width} {canvas_height}">'
        f'<rect width="100%" height="100%" fill="#1e1e2e"/>'
        + spinning_gear(left_x, center_y, input_teeth, module, 0,
                        "steelblue", 1, seconds)
        + spinning_gear(right_x, center_y, output_teeth, module,
                        mesh_rotation, "tomato", -1,
                        seconds * output_teeth / input_teeth)
        + '</svg>'
    )


def gear_image_url(input_teeth: int, output_teeth: int) -> str:
    """Turn the gear picture into a data URL that Image can display.

    ADVANCED TECHNIQUE (not covered in class): quote from urllib.parse
    escapes special characters so the SVG text is safe inside a URL.

    Args:
        input_teeth (int): The number of teeth on the input gear.
        output_teeth (int): The number of teeth on the output gear.
    Returns:
        str: A data URL containing the SVG."""
    return "data:image/svg+xml;utf8," + quote(gear_svg(input_teeth, output_teeth))
def nav_buttons()-> list:
    """Make the navigation buttons shown at the top of every page.
 
    Returns:
        list: The buttons for the home, calculator, history, and about pages."""
    
    return [Button("Home", home_page),
            Button("Calculator", calculator_page),
            Button("History", history_page),
            Button("About", about_page),
            LineBreak()]

@route
def index(state: State) -> Page:
    """Starting route that Drafter loads first; shows the home page.

    Args:
        state (State): The current state of the website
    Returns:
        Page: The home page"""
    return home_page(state)
@route
def home_page(state: State) -> Page:
    """Show the welcome page with links to the other pages
    Args:
        state (State): The current state of the website
    Returns:
        Page: The home page"""
    return Page(state, nav_buttons() + [
        Header("Gear Ratio Calculator"),
        "See how a pair of gears changes speed and torque.",
        "Enter a speed, a torque, and the teeth on each gear.",
        LineBreak(),
        Button("Start Calculating", calculator_page),
        Button("How It Works", about_page),
    ])
        

@route
def calculator_page(state: State) -> Page:
    """Page where users input input speed, input torque and teeth count
    Args:
        state (State): The current state of the website
    Returns:
        Page: The calculator page"""
    return Page(state, nav_links() + [
        Header("Calculator"),"Input speed (RPM):",
        TextBox("input_speed", str(state.input_speed)),
        "Input torque (Nm):",
        TextBox("input_torque", str(state.input_torque)),
        "Number of teeth on input gear:",
        TextBox("input_teeth", str(state.input_teeth)),
        "Number of teeth on output gear:",
        TextBox("output_teeth", str(state.output_teeth)),
        Button("Calculate", calculate_gear_ratio),
        Image(gear_image_url(state.input_teeth, state.output_teeth)),
    ])
        
def nav_links() -> list:
    """Make navigation links that don't submit form fields.

    Returns:
        list: The links for the home, history, and about pages."""
    return [Link("Home", home_page),
            Link("History", history_page),
            Link("About", about_page),
            LineBreak()]
@route
def calculate_gear_ratio(state: State, input_speed: str, input_torque: str,
                         input_teeth: str, output_teeth: str) -> Page:
    """Checks the inputs, calculates the ratio, and save the results to the history
    Args:
        state (State): The current state of the website
        input_speed (str): The speed text typed by the user
        input_torque (str): The torque text typed by the user
        input_teeth (str): The input gear teeth text typed by the user
        output_teeth (str): The output gear teeth text typed by the user
    Returns:
        Page: The results page if the inputs are valid if not a page with an error"""
    error = ""
    if not speed_is_valid(input_speed):
        error = "Enter Valid Input Speed"
    elif not torque_is_valid(input_torque):
        error = "Enter Valid Input Torque"
    elif not teeth_are_valid(input_teeth):
        error = "Enter Valid Input Gear Teeth"
    elif not teeth_are_valid(output_teeth):
        error = "Enter Valid Output Gear Teeth"
    if error != "":
        return Page(state, nav_buttons() + [
            Header("Calculator"),
            error,
            Button("Try Again", calculator_page),])
    state.input_speed = float(input_speed)
    state.input_torque = float(input_torque)
    state.input_teeth = int(input_teeth)
    state.output_teeth = int(output_teeth)
    state.gear_ratio = gear_ratio(state.input_teeth, state.output_teeth)
    state.history.append(GearCalculation(
        state.input_speed, state.input_torque,
        state.input_teeth, state.output_teeth, state.gear_ratio,
        output_speed(state.input_speed, state.gear_ratio),
        output_torque(state.input_torque, state.gear_ratio)))
    return results_page(state)
    
        
@route
def results_page(state: State) -> Page:
    """Show the gear ratio, output speed, and output torque based on what was inputted
    Args:
        state (State): The current state of the website.
    Returns:
        Page: The results page."""
    if len(state.history) == 0:
        return Page(state, nav_buttons() + [
            Header("Results"),
            "You have not calculated anything yet.",])
    latest = state.history[-1]
    return Page(state, nav_buttons() + [
        Header("Results"),
        "Gear ratio: " + str(round(latest.gear_ratio, 3)),
        "Output speed: " + str(round(latest.output_speed, 2)) + " RPM",
        "Output torque: " + str(round(latest.output_torque, 2)) + " Nm",
        describe_ratio(latest.gear_ratio),
        Image(gear_image_url(latest.input_teeth, latest.output_teeth)),
        Button("Calculate Again", calculator_page),
    ])

    
    

@route
def history_page(state: State) -> Page:
    """Show every saved calculation and the highest gear ratio
 
    Args:
        state (State): The current state of the website
    Returns:
        Page: The history page"""
    if len(state.history) == 0:
        return Page(state, nav_buttons() + [
            Header("History"), "No calculations yet."])
    return Page(state, nav_buttons() + [
        Header("History"),
        Table(history_rows(state.history)),
        "Highest gear ratio: " + str(round(highest_ratio(state.history), 3)),
        Button("Clear History", clear_history),
    ])

    


@route
def about_page(state: State) -> Page:
    """Explain what a gear ratio is and how the calculations work
 
    Args:
        state (State): The current state of the website
    Returns:
        Page: The about page."""
    return Page(state, nav_buttons() + [
        Header("About"),"A gear ratio compares the teeth on two gears.",
        "Gear ratio = output teeth / input teeth",
        "Output speed = input speed / gear ratio",
        "Output torque = input torque * gear ratio",
        "A ratio above 1 slows the output and increases torque.",
        "A ratio below 1 speeds up the output and decreases torque.",
    ])

@route
def clear_history(state: State) -> Page: 
    """Delete all saved calculations.
 
    Args:
        state (State): The current state of the website.
    Returns:
        Page: The history page, now empty.
    """
    state.history = []
    return history_page(state)
#Unit Tests
#is_number:
assert_equal(is_number("12"), True)
assert_equal(is_number("0"), True)
assert_equal(is_number("-4"), False)
assert_equal(is_number(""), False)
assert_equal(is_number(".5"), True)
#gear_ratio
assert_equal(gear_ratio(20, 40), 2.0)
assert_equal(gear_ratio(40, 20), 0.5)
assert_equal(gear_ratio(10, 10), 1.0)
#output_speed
assert_equal(output_speed(1000.0, 2.0), 500.0)
assert_equal(output_speed(1000.0, 1.0), 1000.0)
#output_torque
assert_equal(output_torque(10.0, 1.0), 10.0)
assert_equal(output_torque(10.0, 2.0), 20.0)
#speed_is_valid
assert_equal(speed_is_valid(""), False)
assert_equal(speed_is_valid("1000"), True)
assert_equal(speed_is_valid("100001"), False)
assert_equal(speed_is_valid("0"), False)
assert_equal(speed_is_valid("-1"), False)
#torque_is_valid
assert_equal(torque_is_valid("10"), True)
assert_equal(torque_is_valid("0"), False)
assert_equal(torque_is_valid(" "), False)
assert_equal(torque_is_valid("-1"), False)
#teeth_is_valid
assert_equal(teeth_are_valid("20"), True)
assert_equal(teeth_are_valid(""), False)
assert_equal(teeth_are_valid("0"), False)
#describe_ratio
assert_equal(describe_ratio(2.0),
             "The output gear is slower than the input gear, with more torque.")
assert_equal(describe_ratio(0.5),
             "The output gear is faster than the input gear, with less torque.")
assert_equal(describe_ratio(1.0), "The speed and torque do not change.")
#highest_ratio
assert_equal(highest_ratio([]), 0.0)
assert_equal(highest_ratio([GearCalculation(1.0, 1.0, 12, 6, 0.5, 2.0, 0.5)]),
             0.5)
#history_rows
assert_equal(history_rows([GearCalculation(1.0, 2.0, 6, 12, 2.0, 0.5, 4.0)]),
             [["Input RPM", "Input Nm", "Input Teeth", "Output Teeth",
               "Gear Ratio"],
              ["1.0", "2.0", "6", "12", "2.0"]])
#nav_buttons
assert_equal(nav_buttons(),
             [Button("Home", home_page), Button("Calculator", calculator_page),
              Button("History", history_page), Button("About", about_page),
              LineBreak()])
#nav_links
assert_equal(len(nav_links()), 4)
assert_equal(isinstance(nav_links()[0], Link), True)
assert_equal(isinstance(nav_links()[1], Link), True)
assert_equal(isinstance(nav_links()[2], Link), True)
assert_equal(isinstance(nav_links()[3], LineBreak), True)

#gear_points                 
assert_equal(len(gear_points(0, 0, 10, 5, 0).split(" ")), 40)
#spinning_gear
test_gear = spinning_gear(100, 100, 10, 5, 0, "steelblue", 1, 4.0)

assert_equal("<polygon" in test_gear, True)
#gear_svg
assert_equal("<svg" in gear_svg(20, 40), True)
#gear_image_url
assert_equal(gear_image_url(20, 40).startswith("data:image/svg+xml"), True)
#index
assert_equal(index(State(1000.0, 10.0, 20, 40, 2.0, [])),
             home_page(State(1000.0, 10.0, 20, 40, 2.0, [])))
#home_page
assert_equal(home_page(State(1000.0, 10.0, 20, 40, 2.0, [])),
             Page(State(1000.0, 10.0, 20, 40, 2.0, []), nav_buttons() + [
                 Header("Gear Ratio Calculator"),
                 "See how a pair of gears changes speed and torque.",
                 "Enter a speed, a torque, and the teeth on each gear.",
                 LineBreak(),
                 Button("Start Calculating", calculator_page),
                 Button("How It Works", about_page)]))
#calculator_page
assert_equal(calculator_page(State(250.0, 3.5, 30, 15, 0.5, [])),
             Page(State(250.0, 3.5, 30, 15, 0.5, []), nav_links() + [
                 Header("Calculator"), "Input speed (RPM):",
                 TextBox("input_speed", "250.0"),
                 "Input torque (Nm):",
                 TextBox("input_torque", "3.5"),
                 "Number of teeth on input gear:",
                 TextBox("input_teeth", "30"),
                 "Number of teeth on output gear:",
                 TextBox("output_teeth", "15"),
                 Button("Calculate", calculate_gear_ratio),
                 Image(gear_image_url(30, 15))]))
#calculate_gear_ratio
assert_equal(
    calculate_gear_ratio(State(1000.0, 10.0, 20, 40, 2.0, []),
                         "600", "20", "10", "30"),
    Page(State(600.0, 20.0, 10, 30, 3.0,
               [GearCalculation(600.0, 20.0, 10, 30, 3.0, 200.0, 60.0)]),
         nav_buttons() + [
             Header("Results"),
             "Gear ratio: 3.0",
             "Output speed: 200.0 RPM",
             "Output torque: 60.0 Nm",
             "The output gear is slower than the input gear, with more torque.",
             Image(gear_image_url(10, 30)),
             Button("Calculate Again", calculator_page)]))
#invalid_input
assert_equal(
    calculate_gear_ratio(State(1000.0, 10.0, 20, 40, 2.0, []),
                         "abc", "20", "10", "30"),
    Page(State(1000.0, 10.0, 20, 40, 2.0, []), nav_buttons() + [
        Header("Calculator"), "Enter Valid Input Speed",
        Button("Try Again", calculator_page)]))
#results_page
assert_equal(results_page(State(1000.0, 10.0, 20, 40, 2.0, [])),
             Page(State(1000.0, 10.0, 20, 40, 2.0, []), nav_buttons() + [
                 Header("Results"),
                 "You have not calculated anything yet."]))
#history_page
assert_equal(history_page(State(1000.0, 10.0, 20, 40, 2.0, [])),
             Page(State(1000.0, 10.0, 20, 40, 2.0, []), nav_buttons() + [
                 Header("History"), "No calculations yet."]))
#about_page
assert_equal(about_page(State(1000.0, 10.0, 20, 40, 2.0, [])),
             Page(State(1000.0, 10.0, 20, 40, 2.0, []), nav_buttons() + [
                 Header("About"),
                 "A gear ratio compares the teeth on two gears.",
                 "Gear ratio = output teeth / input teeth",
                 "Output speed = input speed / gear ratio",
                 "Output torque = input torque * gear ratio",
                 "A ratio above 1 slows the output and increases torque.",
                 "A ratio below 1 speeds up the output and decreases torque."]))
#clear_history
assert_equal(
    clear_history(State(1000.0, 10.0, 20, 40, 2.0,
                        [GearCalculation(1000.0, 10.0, 20, 40, 2.0, 500.0, 20.0)])),
    Page(State(1000.0, 10.0, 20, 40, 2.0, []), nav_buttons() + [
        Header("History"), "No calculations yet."]))
assert_equal(clear_history(State(1000.0, 10.0, 20, 40, 2.0, [])),
             Page(State(1000.0, 10.0, 20, 40, 2.0, []), nav_buttons() + [
                 Header("History"), "No calculations yet."]))
start_server(State(1000.0, 10.0, 20, 40, 2.0, []))    
