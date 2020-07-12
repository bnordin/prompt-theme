#!/usr/bin/python3
"""Prompt Theme

Description
-----------

This scripts takes a theme file in JSON format and prints a PS1-formatted string to stdout.

Liscense
--------
Promt-Theme is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Promt-Theme is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Promt-Theme.  If not, see <https://www.gnu.org/licenses/>.

References
----------
- Chris Titus Tech
  - https://raw.githubusercontent.com/ChrisTitusTech/scripts/master/fancy-bash-promt.sh
- Andres Gongora
  - https://github.com/andresgongora/bash-tools
- WOLFMAN'S color bash prompt
  - https://wiki.chakralinux.org/index.php?title=Color_Bash_Prompt#Wolfman.27s
- https://gist.github.com/MicahElliott/719710
- https://jonasjacek.github.io/colors/
"""

import re
import sys
import argparse
import json
import copy
import os

############
# General
############

def main(argv: list):
    """Program entry point. Loads the theme file and prints the PS1 prompt to stdout

    Parameters
    ----------
    argv : list
        The program arguments

    Notes
    -----
    Prints the new prompt to stdout
    """

    options = processOptions(argv)
    theme = options['theme']
    theme = validateTheme(theme)
    promptStr = getPromptStr(theme)
    printPrompt(promptStr)
    sys.exit(0)

def processOptions(argv: list)->dict:
    """Parse the program parameters and load results into a dictionary

    Parameters
    ----------
    argv : list
        The program arguments

    Returns
    -------
    dictionary
        The JSON theme
    """

    parser = argparse.ArgumentParser(
        description='This scripts takes a theme file in JSON format and prints a PS1-formatted string to stdout.')

    parser.add_argument(
        '--theme',
        '-t',
        type=str,
        required=True,
        help="The theme in JSON format"
    )
    args = parser.parse_args()

    themefile = args.theme

    if not os.path.isfile(themefile):
        errorExit('Could not find theme file')

    theme = None

    try:
        jsonFile = open(themefile, 'r')
        theme = json.load(jsonFile)
    except:
        print('ERROR processing theme',file=sys.stderr)
    finally:
        jsonFile.close()

    if theme == None:
        sys.exit(1)
    options={
        "theme": theme
    }
    return options

def errorExit(message: str):
    """Print the given error message and exit the script with an error code

    Parameters
    ----------
    message : str
        The message to print
    """

    print('ERROR: %s' % (message), file=sys.stderr)
    sys.exit(1)

############
# Theme
############

def validateTheme(theme: list) -> list:
    """Validate the theme components and fill in any gaps with defaults

    Parameters
    ----------
    theme : list
        The theme components

    Returns
    -------
    list
        The updated theme components
    """

    if (len(theme) == 0):
        errorExit('JSON outer element must be an array of one or more elements')

    nTheme = copy.deepcopy(theme)
    for iC,component in enumerate(nTheme):
        nTheme[iC] = validateComponent(component)
    return nTheme

def validateComponent(component: dict) -> dict:
    """Validate an individual theme component and fill in any gaps with defaults

    Parameters
    ----------
    component : dict
        The theme component

    Returns
    -------
    dict
        The updated theme component
    """

    if (type(component) != dict):
        errorExit('One of the elements is not a valid JSON object')
    nComponent = copy.deepcopy(component)
    if 'text' not in nComponent:
        nComponent['text']=None

    if 'env' not in nComponent:
        nComponent['env']=None

    if (nComponent['env'] != None
        and nComponent['text'] == None
    ):
        nComponent['type']='env'

    if 'type' not in nComponent or nComponent['type'] == None:
        nComponent['type'] = 'text'

    if (nComponent['type'].lower() != 'text'
        and nComponent['type'].lower() != 'env'
        and nComponent['type'].lower() != 'reset'
        ):
        errorExit('Invalid type: ' + nComponent['type'])

    if 'color' not in nComponent:
        nComponent['color'] = None

    if nComponent['color'] != None:
        if 'depth' not in nComponent['color']:
            nComponent['color']['depth']=4
        if 'fg' not in nComponent['color']:
            nComponent['color']['fg']=None
        validateColor(nComponent['color']['fg'])
        if 'bg' not in nComponent['color']:
            nComponent['color']['bg'] = None
        validateColor(nComponent['color']['bg'])
        if 'effect' not in nComponent['color']:
            nComponent['color']['effect'] = None
        # TODO: validate effect
        if (nComponent['color']['fg'] == None
            and nComponent['color']['bg'] == None
            and nComponent['color']['effect'] == None
        ):
            nComponent['color']=None

    return nComponent

def validateColor(color: str) -> bool:
    """Validate a color value

    Parameters
    ----------
    color : str
        The color

    Returns
    -------
    bool
        Indicator as to the color's validity

    Notes
    -----
    Needs work, so disabled for now
    """

    1==1
    #if color.isdigit()
    #    if color < 0 or color > 255:
    #        errorExit('Color outside expected range of 0 to 255 (%s)' % color)
    #todo: names

def getPromptStr(theme: list) -> str:
    """Get a prompt string from the theme

    Parameters
    ----------
    theme : list
        The theme components

    Returns
    -------
    str
        The prompt string
    """

    promptStr=''
    for component in theme:
        text=getComponentStr(component)
        if text!=None:
            promptStr+=text

    return promptStr

def getComponentStr(component: dict) -> str:
    """Get a prompt string from the theme component

    Parameters
    ----------
    component : dict
        The theme component

    Returns
    -------
    str
        The prompt string
    """

    type = component['type'].lower()
    text = component['text']
    hasColor = (component['color'] != None)
    if type == 'reset':
        text = formatResetText()
        hasColor = False
    elif type == 'env':
        text = os.environ[component['env']]

    if text != None and hasColor:
        text = formatColor(component['color'])+text

    return text

############
# Color
############

def getColorCodeFromNameDepth(colorName: str, colorDepth: int)->int:
    """Return the color escape code from the color name and bit depth

    Parameters
    ----------
    colorName : str
        The color name

    colorDepth : int
        The color bit depth (4 or 8)

    Returns
    -------
    int
        The color escape code
    """

    if colorDepth == 8:
        return COLOR_8BIT_D['nameMap'][colorName]
    else:
        return COLOR_4BIT_D['nameMap'][colorName]

def getEffectCodeFromName(effectName: str) -> int:
    """Return the effect escape code from the given name

    Parameters
    ----------
    effectName : str
        The effect name

    Returns
    -------
    int
        The effect escape code
    """

    if effectName == None:
        return None

    eName = effectName.upper()
    code = None

    if   (eName ==      'NONE'): code = 0
    elif (eName ==      'BOLD'): code = 1
    elif (eName ==       'DIM'): code = 2
    elif (eName == 'UNDERLINE'): code = 4
    elif (eName ==     'BLINK'): code = 5
    elif (eName ==    'INVERT'): code = 7
    elif (eName ==    'HIDDEN'): code = 8
    else: errorExit('Unrecognized effect name')

    return code

def getFontFormat(fgColor: str, bgColor: str, effect: int) -> str:
    """Return the prompt format string for the given colors and effect

    Parameters
    ----------
    fgColor : str
        The foreground color format

    bgColor : str
        The background color format

    effect : int
        The effect escape code

    Returns
    -------
    str
        The combined prompt format
    """

    formatStr = '\\[\\033['
    formats = []
    if effect != None:
        formats.append(str(effect))
    if fgColor != None:
        formats.append(str(fgColor))
    if bgColor != None:
        formats.append(str(bgColor))

    formatStr += ';'.join(formats) + 'm\\]'

    return formatStr

def formatColor(color:dict) -> str:
    """Return the prompt format string for the component color definition

    Parameters
    ----------
    color : dict
        The component color definition

    Returns
    -------
    str
        The combined prompt format
    """

    fgColor = getColorCode(color['fg'],'FG',color['depth'])
    bgColor = getColorCode(color['bg'], 'BG',color['depth'])
    effect = getEffectCodeFromName(color['effect'])

    return getFontFormat(fgColor,bgColor,effect)

def getColorCode(color:str,type: str,depth:int) -> str:
    """Return the color format for the corresponding color definiton

    Parameters
    ----------
    color : str
        The color code or name

    type : str
        FG or BG for foreground or background respectively

    depth : int
        The color bit depth

    Returns
    -------
    str
        The color's prompt format string
    """

    code = None
    if (color != None):
        colorRaw = color.lower()
        if len(colorRaw) == 7 and colorRaw[:1] == '#':
            code = getColorCodeFromNumberTypeDepth(
                getBestColorFromHexDepth(colorRaw[1:],depth), type, depth)
        elif colorRaw[:3].lower() == 'rgb':
            code = getColorCodeFromNumberTypeDepth(
                getBestColorFromRgbDepth(colorRaw[4:-1],depth), type, depth)
        elif (colorRaw.isdigit()):
            code = getColorCodeFromNumberTypeDepth(
                colorRaw, type, depth)
        else:
            code = getColorCodeFromNumberTypeDepth(
                getColorCodeFromNameDepth(colorRaw, depth), type, depth)
    return code


def getBestColorFromHexDepth(hexC: str, depth: int) -> int:
    """Return the best color code from the given hex RGB value

    Parameters
    ----------
    hexC : str
        The color code in 6-digit hex format

    depth : int
        The color bit depth (only 8 is supported)

    Returns
    -------
    int
        The color escape code
    """

    if depth != 8:
        errorExit('Hex conversion only supported on 8-bit color depth')

    r = hexC[:2].lower()
    g = hexC[2:-2].lower()
    b = hexC[-2:].lower()
    if r == g and g == b:
        return COLOR_8BIT_D['hexMap'][('#%s%s%s' % (COLOR_8BIT_D['bestGreyHex'][r], COLOR_8BIT_D['bestGreyHex'][g], COLOR_8BIT_D['bestGreyHex'][b]))]
    else:
        return COLOR_8BIT_D['hexMap'][('#%s%s%s' % (COLOR_8BIT_D['bestHex'][r], COLOR_8BIT_D['bestHex'][g], COLOR_8BIT_D['bestHex'][b]))]


def getBestColorFromRgbDepth(rgbC:str, depth: int) -> int:
    """Return the best color code from the given rgb value

    Parameters
    ----------
    hexC : str
        The color code in rgb(r,g,b) format

    depth : int
        The color bit depth (only 8 is supported)

    Returns
    -------
    int
        The color escape code
    """

    if depth != 8:
        errorExit('RGB conversion only supported on 8-bit color depth')

    rgb = rgbC.split(',')
    r = rgb[0]
    g = rgb[1]
    b = rgb[2]
    if r == g and g == b:
        return COLOR_8BIT_D['rgbMap'][ ( 'rgb(%s,%s,%s)' % ( COLOR_8BIT_D['bestGreyRgb'][int(r)],COLOR_8BIT_D['bestGreyRgb'][int(g)],COLOR_8BIT_D['bestGreyRgb'][int(b)]) ) ]
    else:
        return COLOR_8BIT_D['rgbMap'][ ( 'rgb(%s,%s,%s)' % ( COLOR_8BIT_D['bestRgb'][int(r)],COLOR_8BIT_D['bestRgb'][int(g)],COLOR_8BIT_D['bestRgb'][int(b)]) ) ]


def getColorCodeFromNumberTypeDepth(code: int,type: str, depth: int) -> str:
    """Return the best color code from the given code

    Parameters
    ----------
    code : int
        The color code (0-255)

    type : str
        FG or BG for foreground or background respectively

    depth : int
        The color bit depth

    Returns
    -------
    int
        The color escape code
    """

    typeC = 38
    offset = 30
    if (type == 'BG'):
        typeC = 48
        offset = 40
    iCode = int(code)
    if iCode == DEFAULT_COLOR:
        return str(9 + offset)
    elif depth == 8:
        return '%s;5;%s' % (typeC, code)
    else:
        return iCode + offset

def getColor8BitLookupDict() -> dict:
    """Return an 8-bit color code lookup dictionary

    Returns
    -------
    dict
        The 8-bit color code lookup dictionary
    """

    searchColors=[
        { "colorId":   0, "name": "Black"            , "rgb": {"r":   0,"g":   0,"b":   0} },
        { "colorId":   1, "name": "Maroon"           , "rgb": {"r": 128,"g":   0,"b":   0} },
        { "colorId":   2, "name": "Green"            , "rgb": {"r":   0,"g": 128,"b":   0} },
        { "colorId":   3, "name": "Olive"            , "rgb": {"r": 128,"g": 128,"b":   0} },
        { "colorId":   4, "name": "Navy"             , "rgb": {"r":   0,"g":   0,"b": 128} },
        { "colorId":   5, "name": "Purple"           , "rgb": {"r": 128,"g":   0,"b": 128} },
        { "colorId":   6, "name": "Teal"             , "rgb": {"r":   0,"g": 128,"b": 128} },
        { "colorId":   8, "name": "Grey"             , "rgb": {"r": 128,"g": 128,"b": 128} },
        { "colorId":   9, "name": "Red"              , "rgb": {"r": 255,"g":   0,"b":   0} },
        { "colorId":  10, "name": "Lime"             , "rgb": {"r":   0,"g": 255,"b":   0} },
        { "colorId":  11, "name": "Yellow"           , "rgb": {"r": 255,"g": 255,"b":   0} },
        { "colorId":  12, "name": "Blue"             , "rgb": {"r":   0,"g":   0,"b": 255} },
        { "colorId":  13, "name": "Fuchsia"          , "rgb": {"r": 255,"g":   0,"b": 255} },
        { "colorId":  14, "name": "Aqua"             , "rgb": {"r":   0,"g": 255,"b": 255} },
        { "colorId":  15, "name": "White"            , "rgb": {"r": 255,"g": 255,"b": 255} },
        { "colorId":  16, "name": "Grey0"            , "rgb": {"r":   0,"g":   0,"b":   0} },
        { "colorId":  17, "name": "NavyBlue"         , "rgb": {"r":   0,"g":   0,"b":  95} },
        { "colorId":  18, "name": "DarkBlue"         , "rgb": {"r":   0,"g":   0,"b": 135} },
        { "colorId":  19, "name": "Blue3"            , "rgb": {"r":   0,"g":   0,"b": 175} },
        { "colorId":  20, "name": "Blue3"            , "rgb": {"r":   0,"g":   0,"b": 215} },
        { "colorId":  21, "name": "Blue1"            , "rgb": {"r":   0,"g":   0,"b": 255} },
        { "colorId":  22, "name": "DarkGreen"        , "rgb": {"r":   0,"g":  95,"b":   0} },
        { "colorId":  23, "name": "DeepSkyBlue4"     , "rgb": {"r":   0,"g":  95,"b":  95} },
        { "colorId":  24, "name": "DeepSkyBlue4"     , "rgb": {"r":   0,"g":  95,"b": 135} },
        { "colorId":  25, "name": "DeepSkyBlue4"     , "rgb": {"r":   0,"g":  95,"b": 175} },
        { "colorId":  26, "name": "DodgerBlue3"      , "rgb": {"r":   0,"g":  95,"b": 215} },
        { "colorId":  27, "name": "DodgerBlue2"      , "rgb": {"r":   0,"g":  95,"b": 255} },
        { "colorId":  28, "name": "Green4"           , "rgb": {"r":   0,"g": 135,"b":   0} },
        { "colorId":  29, "name": "SpringGreen4"     , "rgb": {"r":   0,"g": 135,"b":  95} },
        { "colorId":  30, "name": "Turquoise4"       , "rgb": {"r":   0,"g": 135,"b": 135} },
        { "colorId":  31, "name": "DeepSkyBlue3"     , "rgb": {"r":   0,"g": 135,"b": 175} },
        { "colorId":  32, "name": "DeepSkyBlue3"     , "rgb": {"r":   0,"g": 135,"b": 215} },
        { "colorId":  33, "name": "DodgerBlue1"      , "rgb": {"r":   0,"g": 135,"b": 255} },
        { "colorId":  34, "name": "Green3"           , "rgb": {"r":   0,"g": 175,"b":   0} },
        { "colorId":  35, "name": "SpringGreen3"     , "rgb": {"r":   0,"g": 175,"b":  95} },
        { "colorId":  36, "name": "DarkCyan"         , "rgb": {"r":   0,"g": 175,"b": 135} },
        { "colorId":  37, "name": "LightSeaGreen"    , "rgb": {"r":   0,"g": 175,"b": 175} },
        { "colorId":  38, "name": "DeepSkyBlue2"     , "rgb": {"r":   0,"g": 175,"b": 215} },
        { "colorId":  39, "name": "DeepSkyBlue1"     , "rgb": {"r":   0,"g": 175,"b": 255} },
        { "colorId":  40, "name": "Green3"           , "rgb": {"r":   0,"g": 215,"b":   0} },
        { "colorId":  41, "name": "SpringGreen3"     , "rgb": {"r":   0,"g": 215,"b":  95} },
        { "colorId":  42, "name": "SpringGreen2"     , "rgb": {"r":   0,"g": 215,"b": 135} },
        { "colorId":  43, "name": "Cyan3"            , "rgb": {"r":   0,"g": 215,"b": 175} },
        { "colorId":  44, "name": "DarkTurquoise"    , "rgb": {"r":   0,"g": 215,"b": 215} },
        { "colorId":  45, "name": "Turquoise2"       , "rgb": {"r":   0,"g": 215,"b": 255} },
        { "colorId":  46, "name": "Green1"           , "rgb": {"r":   0,"g": 255,"b":   0} },
        { "colorId":  47, "name": "SpringGreen2"     , "rgb": {"r":   0,"g": 255,"b":  95} },
        { "colorId":  48, "name": "SpringGreen1"     , "rgb": {"r":   0,"g": 255,"b": 135} },
        { "colorId":  49, "name": "MediumSpringGreen", "rgb": {"r":   0,"g": 255,"b": 175} },
        { "colorId":  50, "name": "Cyan2"            , "rgb": {"r":   0,"g": 255,"b": 215} },
        { "colorId":  51, "name": "Cyan1"            , "rgb": {"r":   0,"g": 255,"b": 255} },
        { "colorId":  52, "name": "DarkRed"          , "rgb": {"r":  95,"g":   0,"b":   0} },
        { "colorId":  53, "name": "DeepPink4"        , "rgb": {"r":  95,"g":   0,"b":  95} },
        { "colorId":  54, "name": "Purple4"          , "rgb": {"r":  95,"g":   0,"b": 135} },
        { "colorId":  55, "name": "Purple4"          , "rgb": {"r":  95,"g":   0,"b": 175} },
        { "colorId":  56, "name": "Purple3"          , "rgb": {"r":  95,"g":   0,"b": 215} },
        { "colorId":  57, "name": "BlueViolet"       , "rgb": {"r":  95,"g":   0,"b": 255} },
        { "colorId":  58, "name": "Orange4"          , "rgb": {"r":  95,"g":  95,"b":   0} },
        { "colorId":  59, "name": "Grey37"           , "rgb": {"r":  95,"g":  95,"b":  95} },
        { "colorId":  60, "name": "MediumPurple4"    , "rgb": {"r":  95,"g":  95,"b": 135} },
        { "colorId":  61, "name": "SlateBlue3"       , "rgb": {"r":  95,"g":  95,"b": 175} },
        { "colorId":  62, "name": "SlateBlue3"       , "rgb": {"r":  95,"g":  95,"b": 215} },
        { "colorId":  63, "name": "RoyalBlue1"       , "rgb": {"r":  95,"g":  95,"b": 255} },
        { "colorId":  64, "name": "Chartreuse4"      , "rgb": {"r":  95,"g": 135,"b":   0} },
        { "colorId":  65, "name": "DarkSeaGreen4"    , "rgb": {"r":  95,"g": 135,"b":  95} },
        { "colorId":  66, "name": "PaleTurquoise4"   , "rgb": {"r":  95,"g": 135,"b": 135} },
        { "colorId":  67, "name": "SteelBlue"        , "rgb": {"r":  95,"g": 135,"b": 175} },
        { "colorId":  68, "name": "SteelBlue3"       , "rgb": {"r":  95,"g": 135,"b": 215} },
        { "colorId":  69, "name": "CornflowerBlue"   , "rgb": {"r":  95,"g": 135,"b": 255} },
        { "colorId":  70, "name": "Chartreuse3"      , "rgb": {"r":  95,"g": 175,"b":   0} },
        { "colorId":  71, "name": "DarkSeaGreen4"    , "rgb": {"r":  95,"g": 175,"b":  95} },
        { "colorId":  72, "name": "CadetBlue"        , "rgb": {"r":  95,"g": 175,"b": 135} },
        { "colorId":  73, "name": "CadetBlue"        , "rgb": {"r":  95,"g": 175,"b": 175} },
        { "colorId":  74, "name": "SkyBlue3"         , "rgb": {"r":  95,"g": 175,"b": 215} },
        { "colorId":  75, "name": "SteelBlue1"       , "rgb": {"r":  95,"g": 175,"b": 255} },
        { "colorId":  76, "name": "Chartreuse3"      , "rgb": {"r":  95,"g": 215,"b":   0} },
        { "colorId":  77, "name": "PaleGreen3"       , "rgb": {"r":  95,"g": 215,"b":  95} },
        { "colorId":  78, "name": "SeaGreen3"        , "rgb": {"r":  95,"g": 215,"b": 135} },
        { "colorId":  79, "name": "Aquamarine3"      , "rgb": {"r":  95,"g": 215,"b": 175} },
        { "colorId":  80, "name": "MediumTurquoise"  , "rgb": {"r":  95,"g": 215,"b": 215} },
        { "colorId":  81, "name": "SteelBlue1"       , "rgb": {"r":  95,"g": 215,"b": 255} },
        { "colorId":  82, "name": "Chartreuse2"      , "rgb": {"r":  95,"g": 255,"b":   0} },
        { "colorId":  83, "name": "SeaGreen2"        , "rgb": {"r":  95,"g": 255,"b":  95} },
        { "colorId":  84, "name": "SeaGreen1"        , "rgb": {"r":  95,"g": 255,"b": 135} },
        { "colorId":  85, "name": "SeaGreen1"        , "rgb": {"r":  95,"g": 255,"b": 175} },
        { "colorId":  86, "name": "Aquamarine1"      , "rgb": {"r":  95,"g": 255,"b": 215} },
        { "colorId":  87, "name": "DarkSlateGray2"   , "rgb": {"r":  95,"g": 255,"b": 255} },
        { "colorId":  88, "name": "DarkRed"          , "rgb": {"r": 135,"g":   0,"b":   0} },
        { "colorId":  89, "name": "DeepPink4"        , "rgb": {"r": 135,"g":   0,"b":  95} },
        { "colorId":  90, "name": "DarkMagenta"      , "rgb": {"r": 135,"g":   0,"b": 135} },
        { "colorId":  91, "name": "DarkMagenta"      , "rgb": {"r": 135,"g":   0,"b": 175} },
        { "colorId":  92, "name": "DarkViolet"       , "rgb": {"r": 135,"g":   0,"b": 215} },
        { "colorId":  93, "name": "Purple"           , "rgb": {"r": 135,"g":   0,"b": 255} },
        { "colorId":  94, "name": "Orange4"          , "rgb": {"r": 135,"g":  95,"b":   0} },
        { "colorId":  95, "name": "LightPink4"       , "rgb": {"r": 135,"g":  95,"b":  95} },
        { "colorId":  96, "name": "Plum4"            , "rgb": {"r": 135,"g":  95,"b": 135} },
        { "colorId":  97, "name": "MediumPurple3"    , "rgb": {"r": 135,"g":  95,"b": 175} },
        { "colorId":  98, "name": "MediumPurple3"    , "rgb": {"r": 135,"g":  95,"b": 215} },
        { "colorId":  99, "name": "SlateBlue1"       , "rgb": {"r": 135,"g":  95,"b": 255} },
        { "colorId": 100, "name": "Yellow4"          , "rgb": {"r": 135,"g": 135,"b":   0} },
        { "colorId": 101, "name": "Wheat4"           , "rgb": {"r": 135,"g": 135,"b":  95} },
        { "colorId": 102, "name": "Grey53"           , "rgb": {"r": 135,"g": 135,"b": 135} },
        { "colorId": 103, "name": "LightSlateGrey"   , "rgb": {"r": 135,"g": 135,"b": 175} },
        { "colorId": 104, "name": "MediumPurple"     , "rgb": {"r": 135,"g": 135,"b": 215} },
        { "colorId": 105, "name": "LightSlateBlue"   , "rgb": {"r": 135,"g": 135,"b": 255} },
        { "colorId": 106, "name": "Yellow4"          , "rgb": {"r": 135,"g": 175,"b":   0} },
        { "colorId": 107, "name": "DarkOliveGreen3"  , "rgb": {"r": 135,"g": 175,"b":  95} },
        { "colorId": 108, "name": "DarkSeaGreen"     , "rgb": {"r": 135,"g": 175,"b": 135} },
        { "colorId": 109, "name": "LightSkyBlue3"    , "rgb": {"r": 135,"g": 175,"b": 175} },
        { "colorId": 110, "name": "LightSkyBlue3"    , "rgb": {"r": 135,"g": 175,"b": 215} },
        { "colorId": 111, "name": "SkyBlue2"         , "rgb": {"r": 135,"g": 175,"b": 255} },
        { "colorId": 112, "name": "Chartreuse2"      , "rgb": {"r": 135,"g": 215,"b":   0} },
        { "colorId": 113, "name": "DarkOliveGreen3"  , "rgb": {"r": 135,"g": 215,"b":  95} },
        { "colorId": 114, "name": "PaleGreen3"       , "rgb": {"r": 135,"g": 215,"b": 135} },
        { "colorId": 115, "name": "DarkSeaGreen3"    , "rgb": {"r": 135,"g": 215,"b": 175} },
        { "colorId": 116, "name": "DarkSlateGray3"   , "rgb": {"r": 135,"g": 215,"b": 215} },
        { "colorId": 117, "name": "SkyBlue1"         , "rgb": {"r": 135,"g": 215,"b": 255} },
        { "colorId": 118, "name": "Chartreuse1"      , "rgb": {"r": 135,"g": 255,"b":   0} },
        { "colorId": 119, "name": "LightGreen"       , "rgb": {"r": 135,"g": 255,"b":  95} },
        { "colorId": 120, "name": "LightGreen"       , "rgb": {"r": 135,"g": 255,"b": 135} },
        { "colorId": 121, "name": "PaleGreen1"       , "rgb": {"r": 135,"g": 255,"b": 175} },
        { "colorId": 122, "name": "Aquamarine1"      , "rgb": {"r": 135,"g": 255,"b": 215} },
        { "colorId": 123, "name": "DarkSlateGray1"   , "rgb": {"r": 135,"g": 255,"b": 255} },
        { "colorId": 124, "name": "Red3"             , "rgb": {"r": 175,"g":   0,"b":   0} },
        { "colorId": 125, "name": "DeepPink4"        , "rgb": {"r": 175,"g":   0,"b":  95} },
        { "colorId": 126, "name": "MediumVioletRed"  , "rgb": {"r": 175,"g":   0,"b": 135} },
        { "colorId": 127, "name": "Magenta3"         , "rgb": {"r": 175,"g":   0,"b": 175} },
        { "colorId": 128, "name": "DarkViolet"       , "rgb": {"r": 175,"g":   0,"b": 215} },
        { "colorId": 129, "name": "Purple"           , "rgb": {"r": 175,"g":   0,"b": 255} },
        { "colorId": 130, "name": "DarkOrange3"      , "rgb": {"r": 175,"g":  95,"b":   0} },
        { "colorId": 131, "name": "IndianRed"        , "rgb": {"r": 175,"g":  95,"b":  95} },
        { "colorId": 132, "name": "HotPink3"         , "rgb": {"r": 175,"g":  95,"b": 135} },
        { "colorId": 133, "name": "MediumOrchid3"    , "rgb": {"r": 175,"g":  95,"b": 175} },
        { "colorId": 134, "name": "MediumOrchid"     , "rgb": {"r": 175,"g":  95,"b": 215} },
        { "colorId": 135, "name": "MediumPurple2"    , "rgb": {"r": 175,"g":  95,"b": 255} },
        { "colorId": 136, "name": "DarkGoldenrod"    , "rgb": {"r": 175,"g": 135,"b":   0} },
        { "colorId": 137, "name": "LightSalmon3"     , "rgb": {"r": 175,"g": 135,"b":  95} },
        { "colorId": 138, "name": "RosyBrown"        , "rgb": {"r": 175,"g": 135,"b": 135} },
        { "colorId": 139, "name": "Grey63"           , "rgb": {"r": 175,"g": 135,"b": 175} },
        { "colorId": 140, "name": "MediumPurple2"    , "rgb": {"r": 175,"g": 135,"b": 215} },
        { "colorId": 141, "name": "MediumPurple1"    , "rgb": {"r": 175,"g": 135,"b": 255} },
        { "colorId": 142, "name": "Gold3"            , "rgb": {"r": 175,"g": 175,"b":   0} },
        { "colorId": 143, "name": "DarkKhaki"        , "rgb": {"r": 175,"g": 175,"b":  95} },
        { "colorId": 144, "name": "NavajoWhite3"     , "rgb": {"r": 175,"g": 175,"b": 135} },
        { "colorId": 145, "name": "Grey69"           , "rgb": {"r": 175,"g": 175,"b": 175} },
        { "colorId": 146, "name": "LightSteelBlue3"  , "rgb": {"r": 175,"g": 175,"b": 215} },
        { "colorId": 147, "name": "LightSteelBlue"   , "rgb": {"r": 175,"g": 175,"b": 255} },
        { "colorId": 148, "name": "Yellow3"          , "rgb": {"r": 175,"g": 215,"b":   0} },
        { "colorId": 149, "name": "DarkOliveGreen3"  , "rgb": {"r": 175,"g": 215,"b":  95} },
        { "colorId": 150, "name": "DarkSeaGreen3"    , "rgb": {"r": 175,"g": 215,"b": 135} },
        { "colorId": 151, "name": "DarkSeaGreen2"    , "rgb": {"r": 175,"g": 215,"b": 175} },
        { "colorId": 152, "name": "LightCyan3"       , "rgb": {"r": 175,"g": 215,"b": 215} },
        { "colorId": 153, "name": "LightSkyBlue1"    , "rgb": {"r": 175,"g": 215,"b": 255} },
        { "colorId": 154, "name": "GreenYellow"      , "rgb": {"r": 175,"g": 255,"b":   0} },
        { "colorId": 155, "name": "DarkOliveGreen2"  , "rgb": {"r": 175,"g": 255,"b":  95} },
        { "colorId": 156, "name": "PaleGreen1"       , "rgb": {"r": 175,"g": 255,"b": 135} },
        { "colorId": 157, "name": "DarkSeaGreen2"    , "rgb": {"r": 175,"g": 255,"b": 175} },
        { "colorId": 158, "name": "DarkSeaGreen1"    , "rgb": {"r": 175,"g": 255,"b": 215} },
        { "colorId": 159, "name": "PaleTurquoise1"   , "rgb": {"r": 175,"g": 255,"b": 255} },
        { "colorId": 160, "name": "Red3"             , "rgb": {"r": 215,"g":   0,"b":   0} },
        { "colorId": 161, "name": "DeepPink3"        , "rgb": {"r": 215,"g":   0,"b":  95} },
        { "colorId": 162, "name": "DeepPink3"        , "rgb": {"r": 215,"g":   0,"b": 135} },
        { "colorId": 163, "name": "Magenta3"         , "rgb": {"r": 215,"g":   0,"b": 175} },
        { "colorId": 164, "name": "Magenta3"         , "rgb": {"r": 215,"g":   0,"b": 215} },
        { "colorId": 165, "name": "Magenta2"         , "rgb": {"r": 215,"g":   0,"b": 255} },
        { "colorId": 166, "name": "DarkOrange3"      , "rgb": {"r": 215,"g":  95,"b":   0} },
        { "colorId": 167, "name": "IndianRed"        , "rgb": {"r": 215,"g":  95,"b":  95} },
        { "colorId": 168, "name": "HotPink3"         , "rgb": {"r": 215,"g":  95,"b": 135} },
        { "colorId": 169, "name": "HotPink2"         , "rgb": {"r": 215,"g":  95,"b": 175} },
        { "colorId": 170, "name": "Orchid"           , "rgb": {"r": 215,"g":  95,"b": 215} },
        { "colorId": 171, "name": "MediumOrchid1"    , "rgb": {"r": 215,"g":  95,"b": 255} },
        { "colorId": 172, "name": "Orange3"          , "rgb": {"r": 215,"g": 135,"b":   0} },
        { "colorId": 173, "name": "LightSalmon3"     , "rgb": {"r": 215,"g": 135,"b":  95} },
        { "colorId": 174, "name": "LightPink3"       , "rgb": {"r": 215,"g": 135,"b": 135} },
        { "colorId": 175, "name": "Pink3"            , "rgb": {"r": 215,"g": 135,"b": 175} },
        { "colorId": 176, "name": "Plum3"            , "rgb": {"r": 215,"g": 135,"b": 215} },
        { "colorId": 177, "name": "Violet"           , "rgb": {"r": 215,"g": 135,"b": 255} },
        { "colorId": 178, "name": "Gold3"            , "rgb": {"r": 215,"g": 175,"b":   0} },
        { "colorId": 179, "name": "LightGoldenrod3"  , "rgb": {"r": 215,"g": 175,"b":  95} },
        { "colorId": 180, "name": "Tan"              , "rgb": {"r": 215,"g": 175,"b": 135} },
        { "colorId": 181, "name": "MistyRose3"       , "rgb": {"r": 215,"g": 175,"b": 175} },
        { "colorId": 182, "name": "Thistle3"         , "rgb": {"r": 215,"g": 175,"b": 215} },
        { "colorId": 183, "name": "Plum2"            , "rgb": {"r": 215,"g": 175,"b": 255} },
        { "colorId": 184, "name": "Yellow3"          , "rgb": {"r": 215,"g": 215,"b":   0} },
        { "colorId": 185, "name": "Khaki3"           , "rgb": {"r": 215,"g": 215,"b":  95} },
        { "colorId": 186, "name": "LightGoldenrod2"  , "rgb": {"r": 215,"g": 215,"b": 135} },
        { "colorId": 187, "name": "LightYellow3"     , "rgb": {"r": 215,"g": 215,"b": 175} },
        { "colorId": 188, "name": "Grey84"           , "rgb": {"r": 215,"g": 215,"b": 215} },
        { "colorId": 189, "name": "LightSteelBlue1"  , "rgb": {"r": 215,"g": 215,"b": 255} },
        { "colorId": 190, "name": "Yellow2"          , "rgb": {"r": 215,"g": 255,"b":   0} },
        { "colorId": 191, "name": "DarkOliveGreen1"  , "rgb": {"r": 215,"g": 255,"b":  95} },
        { "colorId": 192, "name": "DarkOliveGreen1"  , "rgb": {"r": 215,"g": 255,"b": 135} },
        { "colorId": 193, "name": "DarkSeaGreen1"    , "rgb": {"r": 215,"g": 255,"b": 175} },
        { "colorId": 194, "name": "Honeydew2"        , "rgb": {"r": 215,"g": 255,"b": 215} },
        { "colorId": 195, "name": "LightCyan1"       , "rgb": {"r": 215,"g": 255,"b": 255} },
        { "colorId": 196, "name": "Red1"             , "rgb": {"r": 255,"g":   0,"b":   0} },
        { "colorId": 197, "name": "DeepPink2"        , "rgb": {"r": 255,"g":   0,"b":  95} },
        { "colorId": 198, "name": "DeepPink1"        , "rgb": {"r": 255,"g":   0,"b": 135} },
        { "colorId": 199, "name": "DeepPink1"        , "rgb": {"r": 255,"g":   0,"b": 175} },
        { "colorId": 200, "name": "Magenta2"         , "rgb": {"r": 255,"g":   0,"b": 215} },
        { "colorId": 201, "name": "Magenta1"         , "rgb": {"r": 255,"g":   0,"b": 255} },
        { "colorId": 202, "name": "OrangeRed1"       , "rgb": {"r": 255,"g":  95,"b":   0} },
        { "colorId": 203, "name": "IndianRed1"       , "rgb": {"r": 255,"g":  95,"b":  95} },
        { "colorId": 204, "name": "IndianRed1"       , "rgb": {"r": 255,"g":  95,"b": 135} },
        { "colorId": 205, "name": "HotPink"          , "rgb": {"r": 255,"g":  95,"b": 175} },
        { "colorId": 206, "name": "HotPink"          , "rgb": {"r": 255,"g":  95,"b": 215} },
        { "colorId": 207, "name": "MediumOrchid1"    , "rgb": {"r": 255,"g":  95,"b": 255} },
        { "colorId": 208, "name": "DarkOrange"       , "rgb": {"r": 255,"g": 135,"b":   0} },
        { "colorId": 209, "name": "Salmon1"          , "rgb": {"r": 255,"g": 135,"b":  95} },
        { "colorId": 210, "name": "LightCoral"       , "rgb": {"r": 255,"g": 135,"b": 135} },
        { "colorId": 211, "name": "PaleVioletRed1"   , "rgb": {"r": 255,"g": 135,"b": 175} },
        { "colorId": 212, "name": "Orchid2"          , "rgb": {"r": 255,"g": 135,"b": 215} },
        { "colorId": 213, "name": "Orchid1"          , "rgb": {"r": 255,"g": 135,"b": 255} },
        { "colorId": 214, "name": "Orange1"          , "rgb": {"r": 255,"g": 175,"b":   0} },
        { "colorId": 215, "name": "SandyBrown"       , "rgb": {"r": 255,"g": 175,"b":  95} },
        { "colorId": 216, "name": "LightSalmon1"     , "rgb": {"r": 255,"g": 175,"b": 135} },
        { "colorId": 217, "name": "LightPink1"       , "rgb": {"r": 255,"g": 175,"b": 175} },
        { "colorId": 218, "name": "Pink1"            , "rgb": {"r": 255,"g": 175,"b": 215} },
        { "colorId": 219, "name": "Plum1"            , "rgb": {"r": 255,"g": 175,"b": 255} },
        { "colorId": 220, "name": "Gold1"            , "rgb": {"r": 255,"g": 215,"b":   0} },
        { "colorId": 221, "name": "LightGoldenrod2"  , "rgb": {"r": 255,"g": 215,"b":  95} },
        { "colorId": 222, "name": "LightGoldenrod2"  , "rgb": {"r": 255,"g": 215,"b": 135} },
        { "colorId": 223, "name": "NavajoWhite1"     , "rgb": {"r": 255,"g": 215,"b": 175} },
        { "colorId": 224, "name": "MistyRose1"       , "rgb": {"r": 255,"g": 215,"b": 215} },
        { "colorId": 225, "name": "Thistle1"         , "rgb": {"r": 255,"g": 215,"b": 255} },
        { "colorId": 226, "name": "Yellow1"          , "rgb": {"r": 255,"g": 255,"b":   0} },
        { "colorId": 227, "name": "LightGoldenrod1"  , "rgb": {"r": 255,"g": 255,"b":  95} },
        { "colorId": 228, "name": "Khaki1"           , "rgb": {"r": 255,"g": 255,"b": 135} },
        { "colorId": 229, "name": "Wheat1"           , "rgb": {"r": 255,"g": 255,"b": 175} },
        { "colorId": 230, "name": "Cornsilk1"        , "rgb": {"r": 255,"g": 255,"b": 215} },
        { "colorId": 231, "name": "Grey100"          , "rgb": {"r": 255,"g": 255,"b": 255} },
    ]
    greyColors=[
        { "colorId":   7, "name": "Silver"           , "rgb": {"r": 192,"g": 192,"b": 192} },
        { "colorId": 232, "name": "Grey3"            , "rgb": {"r":   8,"g":   8,"b":   8} },
        { "colorId": 233, "name": "Grey7"            , "rgb": {"r":  18,"g":  18,"b":  18} },
        { "colorId": 234, "name": "Grey11"           , "rgb": {"r":  28,"g":  28,"b":  28} },
        { "colorId": 235, "name": "Grey15"           , "rgb": {"r":  38,"g":  38,"b":  38} },
        { "colorId": 236, "name": "Grey19"           , "rgb": {"r":  48,"g":  48,"b":  48} },
        { "colorId": 237, "name": "Grey23"           , "rgb": {"r":  58,"g":  58,"b":  58} },
        { "colorId": 238, "name": "Grey27"           , "rgb": {"r":  68,"g":  68,"b":  68} },
        { "colorId": 239, "name": "Grey30"           , "rgb": {"r":  78,"g":  78,"b":  78} },
        { "colorId": 240, "name": "Grey35"           , "rgb": {"r":  88,"g":  88,"b":  88} },
        { "colorId": 241, "name": "Grey39"           , "rgb": {"r":  98,"g":  98,"b":  98} },
        { "colorId": 242, "name": "Grey42"           , "rgb": {"r": 108,"g": 108,"b": 108} },
        { "colorId": 243, "name": "Grey46"           , "rgb": {"r": 118,"g": 118,"b": 118} },
        { "colorId": 244, "name": "Grey50"           , "rgb": {"r": 128,"g": 128,"b": 128} },
        { "colorId": 245, "name": "Grey54"           , "rgb": {"r": 138,"g": 138,"b": 138} },
        { "colorId": 246, "name": "Grey58"           , "rgb": {"r": 148,"g": 148,"b": 148} },
        { "colorId": 247, "name": "Grey62"           , "rgb": {"r": 158,"g": 158,"b": 158} },
        { "colorId": 248, "name": "Grey66"           , "rgb": {"r": 168,"g": 168,"b": 168} },
        { "colorId": 249, "name": "Grey70"           , "rgb": {"r": 178,"g": 178,"b": 178} },
        { "colorId": 250, "name": "Grey74"           , "rgb": {"r": 188,"g": 188,"b": 188} },
        { "colorId": 251, "name": "Grey78"           , "rgb": {"r": 198,"g": 198,"b": 198} },
        { "colorId": 252, "name": "Grey82"           , "rgb": {"r": 208,"g": 208,"b": 208} },
        { "colorId": 253, "name": "Grey85"           , "rgb": {"r": 218,"g": 218,"b": 218} },
        { "colorId": 254, "name": "Grey89"           , "rgb": {"r": 228,"g": 228,"b": 228} },
        { "colorId": 255, "name": "Grey93"           , "rgb": {"r": 238,"g": 238,"b": 238} }
    ]
    nameMap = {}
    rgbMap = {}
    hexMap = {}
    groups = []
    for color in searchColors:
        if color['rgb']['r'] not in groups:
            groups.append(color['rgb']['r'])
        if color['name'].lower() not in nameMap:
            nameMap[color['name'].lower()] = color['colorId']
        rgb = 'rgb(%s,%s,%s)' % (color['rgb']['r'], color['rgb']['g'], color['rgb']['b'])
        if rgb not in rgbMap:
            rgbMap[rgb] = color['colorId']
        hexC = ('#%02X%02X%02X' % (color['rgb']['r'], color['rgb']['g'], color['rgb']['b'])).lower()
        if hexC not in hexMap:
            hexMap[hexC] = color['colorId']

    for color in greyColors:
        if color['name'].lower() not in nameMap:
            nameMap[color['name'].lower()] = color['colorId']
            rgb = 'rgb(%s,%s,%s)' % (color['rgb']['r'], color['rgb']['g'], color['rgb']['b'])
            if rgb not in rgbMap:
                rgbMap[rgb] = color['colorId']
            hexC = ('#%02X%02X%02X' % (color['rgb']['r'], color['rgb']['g'], color['rgb']['b'])).lower()
            if hexC not in hexMap:
                hexMap[hexC] = color['colorId']

    bestRgb={}
    bestHex={}
    bestGreyRgb={}
    bestGreyHex={}
    for i in range(256):
        bI = None
        for iC in groups:
            if (bI == None or abs(iC-i) < abs(bI-i)):
                bI = iC
        bestRgb[int(i)] = int(bI)
        bestHex[('%02X' % i).lower() ] = ('%02X' % (bI)).lower()

        for color in greyColors:
            iC = color['rgb']['r']
            if (bI == None or abs(iC-i) < abs(bI-i)):
                bI = iC
        bestGreyRgb[int(i)] = int(bI)
        bestGreyHex[('%02X' % i).lower()] = ('%02X' % (bI)).lower()

    nameMap['default'] = DEFAULT_COLOR

    return {
        'nameMap': nameMap,
        'rgbMap': rgbMap,
        'hexMap': hexMap,
        'bestRgb': bestRgb,
        'bestHex': bestHex,
        'bestGreyRgb': bestGreyRgb,
        'bestGreyHex': bestGreyHex
    }


def getColor4BitLookupDict() -> dict:
    """Return a 4-bit color code lookup dictionary

    Returns
    -------
    dict
        The 4-bit color code lookup dictionary
    """

    searchColors = [
        {"colorId":   0, "name": "Black"},
        {"colorId":   1, "name": "Red"},
        {"colorId":   2, "name": "Green"},
        {"colorId":   3, "name": "Yellow"},
        {"colorId":   4, "name": "Blue"},
        {"colorId":   5, "name": "Magenta"},
        {"colorId":   6, "name": "Cyan"},
        {"colorId":   7, "name": "Light gray"},
        {"colorId":  60, "name": "Dark gray"},
        {"colorId":  61, "name": "Light red"},
        {"colorId":  62, "name": "Light green"},
        {"colorId":  63, "name": "Light yellow"},
        {"colorId":  64, "name": "Light blue"},
        {"colorId":  65, "name": "Light magenta"},
        {"colorId":  66, "name": "Light cyan"},
        {"colorId":  67, "name": "White"},
    ]
    nameMap = {}
    for color in searchColors:
        if color['name'].lower() not in nameMap:
            nameMap[color['name'].lower()] = color['colorId']

    nameMap['default'] = DEFAULT_COLOR

    return {
        'nameMap': nameMap
    }


############
# Reset
############
def formatResetText() -> str:
    """Returns the reset escape code

    Returns
    -------
    str
        The reset escape code
    """

    return '\\[\\033[0m\\]'

############
# System
############
def printPrompt(promptStr: str):
    """Print the new prompt to stdout if it is valid, otherwise print the existing prompt

    Parameters
    ----------
    promptStr: str
        The new prompt
    """

    if promptStr != None and promptStr != '':
        print(promptStr)
    else:
        print(os.environ['PS1'])

DEFAULT_COLOR = -1
COLOR_4BIT_D = getColor4BitLookupDict()
COLOR_8BIT_D = getColor8BitLookupDict()

if __name__ == "__main__":
   main(sys.argv[1:])
