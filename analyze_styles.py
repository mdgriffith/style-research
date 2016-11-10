from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import colorsys
import itertools
import pprint

retrieval_script = None
with open("analyze-style.js") as ANALYZE:
    retrieval_script = ANALYZE.read()


def retrieve(browser, url):
    browser.get(url)
    elements = browser.execute_script(retrieval_script)
    return {"site":url, "elements":elements}


def parent(element):
    return str(element["level"][:-1])

def parent_level(element):
    return str(len(element["level"]))


def is_transparent(rgb):
    color = parse_color(rgb)
    return color[3] == 0

def unique_margins(margin_counts):
    unique_count = 0
    for margin, count in margin_counts.items():
        if "transparent" not in margin:
            unique_count = unique_count + 1
    return unique_count




# Returns a percentage
def do_children_share_same_margin(elements):
    # Group by level
    elements = sorted(elements, key=parent_level)
    elements = sorted(elements, key=parent)
    total_margins = 0
    margin_discrepencies = 0
    counts = []
    for key, group in itertools.groupby(elements, parent):
        # print(key)
        margin_count = {}
        for element in group:
            margins = [0,0,0,0]
            transparent_background = False
            for prop, val in element["style"].items():
                # print(prop)
                if prop == "margin-top":
                    margins[0] = val
                elif prop == "margin-right":
                    margins[1] = val
                elif prop == "margin-bottom":
                    margins[2] = val
                elif prop == "margin-left":
                    margins[3] = val

                if prop == "background-color" and is_transparent(val):
                    transparent_background = True

            if transparent_background:
                margin_key = str(margins) + " - transparent"
            else:
                margin_key = str(margins)

            if margin_key in margin_count:
                margin_count[margin_key] = margin_count[margin_key] + 1
            else:
                margin_count[margin_key] = 1
            

        unique_count = unique_margins(margin_count)
        total_margins = total_margins + unique_count

        if unique_count > 1:
            print("disc")
            pprint.pprint(margin_count)
            margin_discrepencies = margin_discrepencies + (unique_margins(margin_count) - 1)




        counts.append(margin_count)
    # pprint.pprint(counts)
    # print("Disc Styles")
    # print(margin_discrepencies)
    # print("Total Styles")
    # print(total_margins)
    # print("Ratio")
    # print(str(float(margin_discrepencies)/float(total_margins)))
    return {"counts":counts, "discrepencies":margin_discrepencies, "total_margin_species": total_margins}








def parse_color(rgb):
    rgb = rgb.replace("rgb", "")
    rgb = rgb.replace("a", "")
    rgb = rgb.replace("(", "")
    rgb = rgb.replace(")", "")
    color = [ int(c) if i < 3 else float(c) for i, c in enumerate(rgb.split(",")) ]
    if len(color) == 3:
        color.append(1.0)
    return color

def get_hue(color1, color2):
    hls1 = colorsys.rgb_to_hls(color1[0][0], color1[0][1], color1[0][2])
    hls2 = colorsys.rgb_to_hls(color2[0][0], color2[0][1], color2[0][2])
    return int((hls2[0] - hls1[0]) * 1000)

def sort_by_hue(colors):
    return sorted(colors, cmp=get_hue)

# return a list of colors sorted by hue.
def color_palette(elements):
    colors = {}
    for el in elements:
        for name, val in el["style"].items():
            if name in ("color","background-color", "border-color"):
                color = parse_color(val)
                key = str(color)
                if key not in colors:
                    colors[key] = { "rgb":color, "count":1 }
                else:
                    found = colors[key]
                    found["count"] = found["count"] + 1
                    colors[key] = found
    colors = [(color["rgb"], color["count"]) for name, color in colors.items()]
    return sort_by_hue(colors)



# display: static is meaningful if it has 
# a parent of not display:static
# And there is a child of display:absolute amongst other children.
def is_display_static_meaningful(elements):

    statics = []
    displays = {}
    for el in elements:
        found_display = False
        for name, val in el["style"].items():
            if name == "position":
                if val in displays:
                    displays[val] = displays[val] + 1
                else:
                    displays[val] = 1
                found_display = True

            if name == "position" and val == "static":
                statics.append(el)
                break

    #     if not found_display:
    #         pprint.pprint(el["style"])
    # pprint.pprint(displays)

    meaningful_static_count = 0
    statics_considered = len(statics)
    meaningful_static_elements = []
    for static in statics:
        parent = None
        absoluteChild = None
        children = []
        for el in elements:
            if el["level"] == static["level"][:-1]:
                for name, val in el["style"].items():
                    if name == "position" and val in ("absolute", "relative"):
                        parent = el

            if el["level"][:len(static["level"])] == static["level"] and el["level"] != static["level"]:
                
                positioned = False
                for name, val in el["style"].items():
                    if name == "position" and val == "absolute":
                        absoluteChild = el
                    elif name in ("left", "top", "bottom", "right") and val != "auto":
                        positioned = True
                if not positioned:
                    absoluteChild = None

                if positioned:
                    children.append(el)


            # if parent is not None and absoluteChild is not None and len(children) > 1:
                # break
        if parent is not None and absoluteChild is not None and len(children) > 1:
            meaningful_static_elements.append({"child":absoluteChild, "parent":parent, "element":static})
            meaningful_static_count = meaningful_static_count + 1
            # pprint.pprint(absoluteChild["node"])
            # pprint.pprint(absoluteChild["id"])
            # pprint.pprint(absoluteChild["classes"])
            # pprint.pprint(absoluteChild["level"])

            # pprint.pprint(absoluteChild["style"])

    # print "meaniningful static"
    # print meaningful_static_count
    # print "out of"
    # print statics_considered
    # print str(100.0 * (float(meaningful_static_count)/float(statics_considered))) + "%"
    return {"meaningful":meaningful_static_elements, "full_static_element_count":statics_considered}





def font_palette(elements):

    fonts = []

    for el in elements:
        font = { "family" : None
               , "size" : None
               , "weight" : False
               , "italic" : False
               , "line-height" : None
               }

        for name, val in el["style"].items():
            if name == "font-family":
                font["family"] = ", ".join(sorted(val.lower().split(", ")))
            elif name == "font-size":
                font["size"] = val
            elif name == "font-weight":
                font["weight"] = val
            elif name == "line-height":
                font["line-height"] = val
            elif name == "font-style" and (val == "italic" or val == "oblique"):
                font["italic"] = True
        fonts.append(font)


    overview = {}
    for font in fonts:
        if font["family"] in overview:
            counted = False
            # print overview
            for permutation in overview[font["family"]]:
                if permutation["style"] == font:
                    permutation["count"] = permutation["count"] + 1
                    counted = True
                    break

            if not counted:
                 overview[font["family"]].append({"style" : font, "count" : 1 })
                

        else:
            overview[font["family"]] = [{"style" : font, "count" : 1 }]


    unique_sizes = {}
    for name, permutations in overview.items():
        for perm in permutations:
            if (perm["style"]["size"], perm["style"]["line-height"]) in unique_sizes:
                unique_sizes[(perm["style"]["size"], perm["style"]["line-height"])] = unique_sizes[(perm["style"]["size"], perm["style"]["line-height"])] + 1
            else:
                unique_sizes[(perm["style"]["size"], perm["style"]["line-height"])] = 1

    pprint.pprint(len(overview.keys()))
    pprint.pprint(unique_sizes)



def is_display_inline_meaningful(elements):
    total = 0
    meaningful_count = 0
    for el in elements:
        if el["node"] == "svg" or el["node"] == "img" or el["node"] == "iframe":
            continue
        inline = False
        widthOrHeight = False
        for name, val in el["style"].items():
            if name == "display" and val == "inline":
                inline = True
        for name, val in el["style"].items():
            if name in ("width", "height") and val != "auto" and inline:
                # print val
                print "<" + el["node"] + " ." + str(el["classes"]) + " " + name + ":" + str(val) + ">"
                widthOrHeight = True
        if inline and widthOrHeight:
            meaningful_count = meaningful_count + 1

    print meaningful_count







if __name__ == "__main__":
    sites = []
    with open("sites") as SITES:
        sites = [s for s in SITES.read().split("\n") if s != "" and not s.startswith("#")]

    browser = webdriver.Chrome()
    # try:
    style_data = []
    for site in sites:
        print(site)
        data = retrieve(browser, site)
        style_data.append(data)
        # print color_palette(data["elements"])
        # print do_children_share_same_margin(data["elements"])
        # is_display_static_meaningful(data["elements"])
        # font_palette(data["elements"])

        is_display_inline_meaningful(data["elements"])
        print ""
        print ""

    # except Exception as e:
    #     print(e)
    #     browser.quit()
    
    browser.quit()