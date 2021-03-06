from __future__ import division
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import colorsys
import itertools
import pprint
import hashlib
import tinycss
import os.path
import time
import pdb
import block
from bs4 import BeautifulSoup

retrieval_script = None
with open("analyze-style.js") as ANALYZE:
    retrieval_script = ANALYZE.read()


def retrieve(browser, url):
    browser.get(url)
    time.sleep(5)
    parent_html = browser.execute_script("return document.getElementsByTagName('body')[0].innerHTML")
    elements = browser.execute_script(retrieval_script)
    
    
    ## Show console.log messages
    # for entry in browser.get_log('browser'):
        # print(entry)

    for sheet in elements["external_stylesheets"]:
        browser.get(sheet)
        stylesheet = browser.page_source
        if bool(BeautifulSoup(stylesheet, "html.parser").find()):
            html = BeautifulSoup(stylesheet, "html.parser").find("pre")
            style_sheet = html.get_text()


        elements["stylesheet"] = elements["stylesheet"] + "\n\n" + stylesheet

    return {"site":url, "elements":elements, "html": parent_html}


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


def value_variance(pair1, pair2):
    return cmp(len(pair1[1].keys()), len(pair2[1].keys()))



class StyleSet(object):

    def __init__(self, name, elements=None, props=None, named_styles=None):
        """
        :elements: - [{ "style": List {prop:value} }]
        """
        self.name = name
        if named_styles is None:
            named_styles = {}
        self.named_styles = named_styles
        self.items = {}
        self.props = props
        if elements is not None and props is not None:
            self.create(elements, props)

    def create(self, elements, props):

        remove_props = []
        if props[0] == "remove":
            print "removing"
            print props[1]
            remove_props = props[1]
            props = "all"

        for el in elements:
            found = set()
            for prop, val in el["style"].items():
                if prop in remove_props:
                    continue
                if props == "all" or prop in props:
                    found.add((prop, val))
            if len(found) > 0:
                self.add(found, el)


    def __len__(self):
        return len(self.items.keys())

    def add(self, style, el):
        key = frozenset(style)
        if key in self.items:
            self.items[key].append(el)
        else:
            self.items[key] = [ el ]


    def frequency_of_prop(self):
        prop_freq = {}
        for style, elements in self.items.items():
            for prop, val in list(style):
                if prop in prop_freq:
                    if val in prop_freq[prop]:
                        prop_freq[prop][val] = prop_freq[prop][val] + 1
                    else:
                        prop_freq[prop][val] = 1
                else:
                    prop_freq[prop] = {val:1}

        return sorted(prop_freq.items(), cmp=value_variance) 
        # return prop_freq

    def species(self):
        return self.items.keys()

    def species_count(self):
        """In how many styles does this species show up
        """
        counts = []
        for style, elements in self.items.items():
            
            if style in self.named_styles:
                name = self.named_styles[style]
            else:
                name = list(style)

            counts.append((len(elements), name))
        return sorted(counts, key=lambda x: x[0])


    def species_count_brief(self):
        """In how many styles does this species show up
        """
        counts = []
        for style, elements in self.items.items():
            
            counts.append(len(elements))
        return sorted(counts)

    def classes(self):
        return list(set([value["classes"] for value in self.items.values()]))

    def class_counts(self):
        counts = {}
        for elements in self.items.values():
            for el in elements:
                if el["classes"] in counts:
                    counts[el["classes"]] = counts[el["classes"]] + 1
                else:
                    counts[el["classes"]] = 1
        return counts



class StyleAnalysis(object):

    def __init__(self, name):
        self.name = name
        self.style_sets = []

    def add(self, styleset):
        self.style_sets.append(styleset)

    def report_species(self):
        print("")
        print("Analyzing " + self.name)
        for styleset in self.style_sets:
            print("All species of " + styleset.name)
            print(indent(styleset.species()))
            print("")
        print("")

    def report_species_counts(self):
        print("")
        print("Analyzing " + self.name)
        for styleset in self.style_sets:
            print("Species Count " + styleset.name)
            pprint.pprint(styleset.species_count())
            print("")
        print("")

    def report_classes(self):
        print("")
        print("Analyzing " + self.name)
        for styleset in self.style_sets:
            print("All species of " + styleset.name)
            pprint.pprint(indent(styleset.classes()))
            print("")
        print("")

    def report_class_counts(self):
        print("")
        print("Analyzing " + self.name)
        for styleset in self.style_sets:
            print("All species of " + styleset.name)
            pprint.pprint(indent(styleset.class_counts()))
            print("")
        print("")



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
            # print("disc")
            # pprint.pprint(margin_count)
            margin_discrepencies = margin_discrepencies + (unique_margins(margin_count) - 1)
            counts.append(margin_count)
    
    return { "discrepencies":margin_discrepencies, "total_margin_species": total_margins}








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

def renderRgb(color):
    return "rgba(" + str(color[0]) + "," + str(color[1]) + "," + str(color[2]) + "," + str(color[3]) + ")"

def renderAllRgb(colors):
    rendered = []
    for color in colors:
        rendered.append((renderRgb(color[0]), color[1]))
    return rendered

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
    return renderAllRgb(sort_by_hue(colors))



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
    return {"meaningful":meaningful_static_elements, "meaningful_static_count":meaningful_static_count, "full_static_element_count":statics_considered}





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
            key = str((perm["style"]["size"], perm["style"]["line-height"]))
            if key in unique_sizes:
                unique_sizes[key] = unique_sizes[key] + 1
            else:
                unique_sizes[key] = 1

    # pprint.pprint(len(overview.keys()))
    # pprint.pprint(unique_sizes)
    return unique_sizes



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

    return meaningful_count




def indent(stri):
    return "  " + str(stri)

# Is the number of style species greater if these properties are grouped
def factor(elements, props1, props2):
    species1 = get_species("species1", elements, props=props1)
    species2 = get_species("species2", elements, props=props2)
    both = get_species("both", elements, props=props1 + props2)

    total = len(species1) + len(species2)

    print indent(str(len(species1)) + " ++ " + str(len(species2)) + " = " + str(total))
    print indent(len(both))
    print indent("reduction to: " + str((total/len(both)) * 100) + "%")
    return total/len(both)


def largest_factor(elements, all_props):

    reduction = []
    largest = None
    largest_reduction = None
    for i, p1 in enumerate(all_props):

        comparable = []
        for j, p2 in enumerate(all_props):
            if j != i:
                comparable.extend(p2)

        result = factor(elements, p1, comparable)
        reduction.append((result, p1))

    pprint.pprint(reduction)
    return (largest_reduction, largest)




position_named_styles = {
      frozenset([(u'right', u'auto'),
               (u'position', u'static'),
               (u'left', u'auto'),
               (u'float', u'none'),
               (u'top', u'auto'),
               (u'bottom', u'auto')]) : "Null Position - Static"
    , frozenset([(u'right', u'auto'),
               (u'position', u'relative'),
               (u'left', u'auto'),
               (u'float', u'none'),
               (u'top', u'auto'),
               (u'bottom', u'auto')]) : "Null Position - Relative"
    , frozenset([(u'right', u'auto'),
               (u'position', u'absolute'),
               (u'left', u'auto'),
               (u'float', u'none'),
               (u'top', u'auto'),
               (u'bottom', u'auto')]) : "Null Position - Absolute"
    , frozenset([(u'left', u'0px'),
               (u'position', u'relative'),
               (u'top', u'0px'),
               (u'bottom', u'0px'),
               (u'float', u'none'),
               (u'right', u'0px')]) : "Zero Position"
    , frozenset([(u'right', u'auto'),
                   (u'position', u'static'),
                   (u'left', u'auto'),
                   (u'float', u'left'),
                   (u'top', u'auto'),
                   (u'bottom', u'auto')]) : "Float Left"
    , frozenset([(u'right', u'auto'),
                   (u'position', u'static'),
                   (u'left', u'auto'),
                   (u'float', u'right'),
                   (u'top', u'auto'),
                   (u'bottom', u'auto')]) : "Float Right"

    }





# class AggregateCorrelation(object):

#     def __init__(self, elements):

#         unique_styles = set()
#         for el in elements:
#             key = frozenset(el["style"].items())
#             unique_styles.add(key)

#         list_styles = list(unique_styles)
#         self.correlations = {}
#         for style in list_styles:
#             for prop, val in list(style):
#                 for other_style in list_styles:
                    
#             break


#         self.unique_styles = unique_styles

#     def report(self, prop):
#         pass




# If we separate certain concerns, each separation bring sthe following work:
#  * Creation of a new Type to represent that concept
#  * adding a new class binding to your html node
#  * conceptually remembering how the system works vs the old one.
#  * Feels awkward when you have to split a style into multiple styles that aren't being reused.


# Rule of thumb, for a style to be generic
#  * it needs to be reused in at least 3 places
#     * Specifically it needs to be used at least three times in places where it is _not_ correlated.  In other words, having it show up always with another class will make the developer feel weird.
#     * _Mobility of group_ - How many other groups is it seen with and how often
#  * 
# A perfectly mobile species would show up with each species of a separate group the same number of times.
# A perfectly immobile species would only show up with 1 species of another group

# In order to find this, for each species of a group, count the number of species from another group
# A style species is mobile if it shows up with all species from a given other group equally.
# A style group is mobile if all species have this same distribution


def save(filename, data):
    with open('data/{filename}.json'.format(filename=filename), 'w') as RESULTS:
        print("saving data, {filename}".format(filename=filename))
        RESULTS.write(json.dumps(data, indent=2))


def load(filename):
    file_to_load = 'data/{filename}.json'.format(filename=filename)
    if os.path.isfile(file_to_load):
        with open(file_to_load) as RESULTS:
            try:
                print("loading data")
                return json.loads(RESULTS.read())
            except ValueError, e:
                print("Failed to load {e}".format(e =str(e)))
                return None
    else:
        return None






def retrieve_sites(sites):
    browser = webdriver.Chrome()
    results = []
    for site in sites:
        results.append(retrieve(browser, site))
    browser.quit()
    return results


def merge_style(style_list):
    merged = {"props":{}, "tags":{}}
    for style in style_list:
        merged["props"].update(style["props"])
        for tag, count in style["tags"].items():
            if tag in merged["tags"]:
                merged["tags"][tag] = merged["tags"][tag] + count
            else:
                merged["tags"][tag] = count
    return merged

def match_styles(stylesheet, html):
    

    metrics = {}
    soup = BeautifulSoup(html, "html.parser")
    print("Beginning to Tag elements")
    for i, el in enumerate(soup.find_all()):
        el["researchid"] = i


    print("Beginning Style/Node Search")
    nodes = {}
    # nodes => {researchid: [{selector:x, props:{name:val}, tags:{tag:count}}] }
    dead_styles = 0
    total_count = len(stylesheet)
    used_styles = []
    for i, style in enumerate(stylesheet):
        if "selector" in style:
            if style["selector"] == "*":
                continue
            try:
                found = soup.select(style["selector"])
                if found:
                    if len(found) > 0:
                        used_styles.append(style)
                    else:
                        dead_styles = dead_styles + 1
                    for found_node in found:
                        if "style" in found_node:
                            print(found_node["style"])

                        if found_node["researchid"] in nodes:
                            nodes[found_node["researchid"]].append(style)
                        else:
                            nodes[found_node["researchid"]] = [ style]
                else:
                    dead_styles = dead_styles + 1
            except IndexError:
                dead_styles = dead_styles + 1
                continue

    block.say("Used Styles Cognitive Load")
    metrics["cognitive_load"] = cognitive_load(used_styles)
    metrics["dead_styles"] = dead_styles
    metrics["total_styles"] = total_count
    metrics["used_styles"] = len(used_styles)
    print("dead styles: {count}/{total} -> {used}".format(count=dead_styles, total=total_count, used=metrics["used_styles"]))
    print("finished searching for nodes")

    # single_style => { frozen({name:val}) : node_count }
    single_styles = {}
    for found_styles in nodes.values():
        full_style = {}
        for style in found_styles:
            full_style.update(style["props"])

        frozen_style = frozenset(full_style.items())
        if frozen_style in single_styles:
            single_styles[frozen_style] = single_styles[frozen_style] + 1
        else:
            single_styles[frozen_style] = 1

    print("finished combining")
    # organized => [ { "node_counts":int, "props":{name:val}, "tags": {"tag":count} } ]
    organized = []
    for frozen, count in single_styles.items():
        style = {"node_counts": count, "props":{}}
        for prop, val in list(frozen):
            style["props"][prop] = val

        style["tags"] = tag_counts(style["props"])
        organized.append(style)

    metrics["single_style_count"] = len(organized)
    print("single style count: {count}".format(count=metrics["single_style_count"]))

    # # most frequent (property ++ value)
    # property_value_count = {}
    # for style in organized:
        
    #     for key, value in style["props"].items():
    #         k_v = key + value

    #         if k_v in property_value_count:
    #             property_value_count[k_v] = property_value_count[k_v] + 1
    #         else:
    #             property_value_count[k_v] = 1

    # pprint.pprint(sorted(property_value_count.items(), key=lambda tup: tup[1], reverse=True))


    # # {num_tags: num_styles}
    # summarized = {}
    # for style in organized:
    #     num_tags = len(style["tags"].keys())

    #     if num_tags in summarized:
    #         summarized[num_tags] = summarized[num_tags] + 1
    #     else:
    #         summarized[num_tags] = 1

    # pprint.pprint(summarized)

    # ## {num_props: num_styles}
    # # summarized = {}
    # # for style in organized:
    # #     num_props = len(style["props"].keys())

    # #     if num_props in summarized:
    # #         summarized[num_props] = summarized[num_props] + 1
    # #     else:
    # #         summarized[num_props] = 1

    # # pprint.pprint(summarized)


    return { "styles": organized, "metrics": metrics }


def cognitive_load(styles):
    """
    In this case we're defining cognitive load as a metric that combines the following in some way.
      * Number of css classes
      * Size of css classes
      * Complexity of CSS classes (how many categories there are)
    """
    metrics = {}
    metrics["num_classes"] = len(styles)

    sizes = []
    tags = []
    for style in styles:
        sizes.append(len(style["props"]))
        tags.append(len(style["tags"]))
        # [ { "node_counts":int, "props":{name:val}, "tags": {"tag":count} } ]

    metrics["avg_size"] = sum(sizes) / float(len(sizes))
    metrics["avg_complexity"] = sum(tags) / float(len(tags))
    metrics["cognitive_load"] = metrics["num_classes"] * metrics["avg_complexity"]
    block.indent()
    block.pretty(metrics)
    block.dedent()
    return metrics


def common_values(style1, style2, min_common, min_remaining):
    if len(style1.keys()) < min_common + min_remaining:
        return None

    if len(style2.keys()) < min_common + min_remaining:
        return None


    common_props = {}
    for prop, val in style1.items():
        if prop in style2 and style2[prop] == val:
            common_props[prop] = val

    if len(common_props) >= min_common:
        return common_props

    return None



def extract_variations(styles):
    """
    Variations are small styles that capture the differences between styles that are almost the same.

    Find styles that are 1,2, or 3 properties off, while still having properties of their own(min 3?).

    Desired Result:
       A list of variations and how many classes they could be used by.

    """
    variations = set([])
    
    for i, base_style in enumerate(styles):
        for j, other_style in enumerate(styles):
            if i == j:
                continue

            if i > len(styles)/2:
                continue

            common = common_values(base_style["props"], other_style["props"], 2, 3)

            if common:
                variations.add(frozenset(common.items()))

   
    deduped = []
    for vary in list(variations):
        count = 0
        vary_props = dict(list(vary))
        for s in styles:
            if match_variation(s["props"], vary_props):
                count = count + 1

        if count > 4:
            deduped.append({"props":vary_props, "count":count})




    # block.pretty(sorted(deduped, key=lambda k: k['count'], reverse=True) )



    new_styles = []
    for i, base_style in enumerate(styles):
        reduced = remove_variations(base_style, deduped)
        if reduced:
            new_styles.append(reduced)

    block.indent()
    block.say("Vartiaions: {v}".format(v=len(deduped)))
    block.dedent()

    final_style = new_styles + deduped

    for style in final_style:
        style["tags"] = tag_counts(style["props"])
    return final_style



def match_variation(style, var):
    present = True
    for p, v in var.items():
        if p in style and style[p] == v:
            present = True
        else:
            return False
    return present

def remove_variations(style, variations):
    for v in variations:
        style["props"] = remove_v(style["props"], v["props"])
    return style

def remove_v(style, var):
    present = True
    for p, v in var.items():
        if p in style and style[p] == v:
            present = True
        else:
            return style

    for p in var.keys():
        del style[p]

    return style



def separate_layout_position(styles):

    separated_styles = []
    for style in styles:

        new_style = {}
        new_pos = {}
        new_layout = {}
        for prop, val in style["props"].items():
            tag = tag_property(prop)
            if tag == "position":
                new_pos[prop] = val
            elif tag == "layout":
                new_layout[prop] = val
            else:
                new_style[prop] = val

        if new_style:
            separated_styles.append(new_style)

        if new_layout:
            separated_styles.append(new_layout)

        if new_pos:
            separated_styles.append(new_pos)

    frozen = list(set([ frozenset(s.items()) for s in separated_styles ]))

    separate_styles = []
    for froze in frozen:
        props = {}
        for prop, val in list(froze):
            props[prop] = val

        tags = tag_counts(props)
        separate_styles.append({"props":props, "tags": tags})

    return separate_styles








def analyze_css(retrieved_data):
    """

    Parses CSS.

    Does the following analysis:

    Stylesheets
    
        * Style Definition Count
        * Number of True color models
            * Number of variants
        * Number of Layout Models
        * Number of Position Models
        * Number of Font Models


    Computed Styles
        * How are styles combined
            * id + class + inline
        * Meaningful position:static usage
        * 

    New Formation
        * How many classes/what size would they be if there was only one class per style.
        * Some handle on cognitive load?  Something to do with:
            * Number of StyleClasses
            * Size of Style Classes
                * Maybe diversity of properties within
        * Could these "one style" classes be reduced by taking out common parts as a mixin?



    """
    results = []
    parser = tinycss.make_parser("page3", "fonts3")
    for site in retrieved_data:
        metrics = {}
        print("analyzying {site}".format(site = site["site"]))
        metrics["site"] = site["site"]
        css = parser.parse_stylesheet(site["elements"]["stylesheet"])
 
        ## Process styles into a standardized form.
        styles = []
        for parsed_style in css.rules:

            style = {}
            if hasattr(parsed_style, "selector"):
                # pdb.set_trace()
                style["selector"] = parsed_style.selector.as_css()
                # print(parsed_style.selector.as_css())

            # style.column, line, selector
            if hasattr(parsed_style, "declarations"):
                style["props"] = {}
                for prop in parsed_style.declarations:
                    # prop.column, line, name, priority, value
                    # prop.value append as_css column count extend index insert line pop remove reverse sort'
                    style["props"][prop.name] = prop.value.as_css()

                style["props"] = remove_prefixed(style["props"])
                style["tags"] = tag_counts(style["props"])

            styles.append(style)

        ## The Distribution of how many properties are in each style.
        style_definition_sizes = {} # size: count
        for style in styles:
            if "props" in style:
                size = len(style["props"].keys())
                # if size == 2:
                #     pprint.pprint(style["tags"])
                if size in style_definition_sizes:
                    style_definition_sizes[size] = style_definition_sizes[size] + 1
                else:
                    style_definition_sizes[size] = 1
        metrics["size_distribution"] = style_definition_sizes


        # ## Counts of what property names show up with others
        # # {prop: {otherprop: count}}
        # coproperty_frequency = {}
        # for style in styles:
        #     if "props" in style:
        #         property_names = style["props"].keys()
        #         number_of_keys = len(property_names)
        #         lonely = True
        #         if number_of_keys > 1:
        #             lonely = False
        #         for name in property_names:
        #             if name in coproperty_frequency:
        #                 coproperty_frequency[name][0] = coproperty_frequency[name][0] + 1
        #                 if lonely:
        #                     coproperty_frequency[name][2] = coproperty_frequency[name][2] + 1
        #             else:
        #                 if lonely:
        #                     coproperty_frequency[name] = [1, {}, 1]
        #                 else:
        #                     coproperty_frequency[name] = [1, {}, 0]
 

                    
        #             for other in property_names:
        #                 if name == other:
        #                     continue
                       
        #                 if other in coproperty_frequency[name][1]:
        #                     coproperty_frequency[name][1][other] = coproperty_frequency[name][1][other] + 1
        #                 else:
        #                     coproperty_frequency[name][1][other] = 1
                        
        # # KEEEEP
        # # Give the top associated property for every property found
        # # [(association, self_count, lonely_count, prop, top_associated_prop)]
        # colocated = []
        # for prop, counts in coproperty_frequency.items():
        #     self_count = counts[0]
        #     lonely = counts[2]
        #     top_prop = sorted(counts[1].items(), key=lambda tup: tup[1], reverse=True)

        #     association = 0
        #     if len(top_prop) < 1:
        #         top_prop = None
        #         association
        #     else:
        #         top_prop = top_prop[0]
        #         association = top_prop[1] / self_count

        #     colocated.append((association, self_count, lonely, prop, top_prop))

        # colocated = sorted(colocated, key=lambda tup: tup[0])

        # metrics["colocated_properties"] = colocated


        ####################
        # Actual Node Styles (Via Computed Styles)
        ####################
        # pprint.pprint(site["elements"]["computed_styles"][:1])

        matched = match_styles(styles, site["html"])
        metrics["single_styles"] = matched["styles"]
        metrics["style_processing_metrics"] = matched["metrics"]
        block.say("Single Styles Cognitive Load")
        metrics["cognitive_load"] = cognitive_load(matched["styles"])
        # pprint.pprint(matched)


        most_common_tags = {}
        for style in metrics["single_styles"]:
            for tag in style["tags"].keys():
                if tag in most_common_tags:
                    most_common_tags[tag] = most_common_tags[tag] + 1
                else:
                    most_common_tags[tag] = 1
        metrics["most_common_tags"] = most_common_tags

        separated = separate_layout_position(matched["styles"])
        # metrics["separated_styles"] = separated
        block.say("Separated Styles Cognitive Load")
        metrics["cognitive_load_separated"] = cognitive_load(separated)

        with_variations = extract_variations(separated)
        metrics["variations"] = with_variations
        block.say("Extracted Variations Cognitive Load")
        metrics["cognitive_load_variations"] = cognitive_load(with_variations)

        

        # pprint.pprint(with_variations[:10])
        # print("found variations")
        # print(len(with_variations))



        results.append(metrics)
    return results



position = ["position", "left", "right", "top", "bottom", "float"]
layout = ["display"]
color = ["color", "background-color", "border-color"]
basic = ["border-width", "padding", "font-family", "font-weight", "opacity", "text-align"]


# the prefix 'sw-' means "starts with"
tags = {
     "position": ["position", "left", "right", "top", "bottom", "float", "align-self", "flex-basis", "order", "flex-grow", "flex-shrink", "vertical-align", "transform"]
   , "layout": ["display", "flex", "flex-direction", "justify-content", "align-items", "flex-wrap"]
   , "color": ["color", "background-color", "border-color"]
   , "box": ["sw-padding", "sw-margin", "width", "height", "max-width", "min-width","max-height", "min-height", "box-sizing"]
   , "font": ["sw-font", "text-overflow", "sw-text", "line-height", "whitespace"]
   , "border": ["sw-border"]
   , "visibility": ["opacity", "overflow", "visibility"]
   , "background": ["background-image", "background-size", "background-position", "background-repeat"]
}

def tag_counts(props):
    tags = {}
    for name, val in props.items():
        tag = tag_property(name)
        if tag in tags:
            tags[tag] = tags[tag] + 1
        else:
            tags[tag] = 1
    return tags


def tag_property(name):
    for tag, checks in tags.items():
        for check in checks:
            if check.startswith("sw-") and name.startswith(check[3:]):
                return tag
            elif name == check:
                return tag
    return "misc"




# Style Definition -----
# style = {name:val}

prefixes = ["-webkit-", "-moz-", "-o-", "-ms-", "-khtml-"]

def unprefix(name):
    for prefix in prefixes:
        if name.startswith(prefix):
            return name[len(prefix):]
    return name

def remove_prefixed(style):
    """
    This method loses information.  
    If a property is present in prefixed and unprefixed form, the last one mentioned will be kept
    """
    new_style = {}
    for name, val in style.items():
        new_style[unprefix(name)] = val
    return new_style




if __name__ == "__main__":
    sites = []
    with open("sites") as SITES:
        sites = [s for s in SITES.read().split("\n") if s != "" and not s.startswith("#")]


    # # sites = sites[0:1]
    # # Stylesheet is joing into one big stylesheet
    # # retrieved = load("raw-site-data")
    # # if not retrieved:
    retrieved = retrieve_sites(sites)
    #     # save("raw-site-data", retrieved)

    print("retrieved, analyzing")
    # analyzed = load("single-styles")
    # if not analyzed:
    analyzed = analyze_css(retrieved)
    save("single-styles", analyzed)




    # pprint.pprint(analyzed)

    # parse css
    # css analysis



    # browser = webdriver.Chrome()
    # results = []
    # for site in sites:

    #     # analysis = StyleAnalysis(site)

    #     # analysis = {"site":site}
    #     data = retrieve(browser, site)

    #     # pprint.pprint(data)
    #     save(data, "example")
    #     break
        # correlation = AggregateCorrelation(data["elements"])

        

        # all_styles = StyleSet("All Styles", elements=data["elements"], props="all")

        # # freq = all_styles.frequency_of_prop()
        # # pprint.pprint(freq)
        # # print ""
        # # print ""

        # style_count = all_styles.species_count_brief()
        # print "all"
        # print style_count
        # print len(style_count)
        # print ""


        # position_styles = StyleSet("position_species", elements=data["elements"], props=position, named_styles=position_named_styles)
        # style_count = position_styles.species_count()
        # print "position"
        # pprint.pprint(style_count)
        # print len(style_count)
        # print ""


        # all_but_position_styles = StyleSet("all_but_position_species", elements=data["elements"], props=("remove", position))
        # style_count = all_but_position_styles.species_count_brief()
        # print "all but position"
        # print style_count
        # print len(style_count)
        # print ""
        # print ""



        # layout_styles = StyleSet("position_species", elements=data["elements"], props=layout, named_styles=position_named_styles)
        # style_count = layout_styles.species_count()
        # print "layout"
        # pprint.pprint(style_count)
        # print len(style_count)
        # print ""


        # all_but_layout_styles = StyleSet("all_but_layout", elements=data["elements"], props=("remove", layout))
        # style_count = all_but_layout_styles.species_count()
        # print "all but layout"
        # pprint.pprint(style_count)
        # print len(style_count)
        # print ""
        # print ""


        # analysis.add(StyleSet("layout_species", elements=data["elements"], props=layout))
        # analysis.add(StyleSet("style_species", elements=data["elements"], props=basic))
        # analysis.add(StyleSet("all_species", elements=data["elements"], props=layout + position + basic + color))
        # analysis.add(StyleSet("color_species", elements=data["elements"], props=color))
        # analysis.add(StyleSet("position_species", elements=data["elements"], props=position, named_styles=position_named_styles))
        # analysis.add(StyleSet("all_but_layout_species", elements=data["elements"], props=position + basic + color))
        

        # analysis.report_species_counts()

        # print ""
        # print site + " style counts"
        # print len(analysis["all_species"])
        # print indent("Layout counts")
        # print indent(len(analysis["layout_species"]))

        # print indent("All But Layout counts")
        # print indent(len(analysis["all_but_layout_species"]))

        # print indent("Style counts")
        # print indent(len(analysis["style_species"]))

        # print indent("Color counts")
        # print indent(len(analysis["color_species"]))

        # print indent("Position counts")
        # print indent(len(analysis["position_species"]))
        # print indent("Species count")
        # pprint.pprint(analysis["position_species"].species_count())
        # print ""

        # total = len(analysis["layout_species"]) + len(analysis["style_species"]) + len(analysis["color_species"]) + len(analysis["position_species"])

        # print indent("total")
        # print indent(total)

        # print indent("compressed to")
        # print indent(str((total/len(analysis["all_species"])) * 100) + "%")

        # print ""
        # print indent("Position vs Color")
        # factor(data["elements"], position, color)

        # print ""
        # print indent("Layout Vs Non-Layout")
        # factor(data["elements"], layout, position + basic + color)

        # print ""
        # print indent("Basic Vs Color")
        # factor(data["elements"], basic, color)


        # print indent(mobility_factor(data["elements"], [layout, position, basic, color]))
        # print indent(largest_factor(data["elements"], [basic, color, layout, position]))

        # analysis["color_palette"] = color_palette(data["elements"])
        # analysis["children_same_margin"] = do_children_share_same_margin(data["elements"])
        # analysis["meaningful_static_count"] =  is_display_static_meaningful(data["elements"])
        # analysis["font_sizes"] = font_palette(data["elements"])
        # analysis["meaningful_inline_count"] = is_display_inline_meaningful(data["elements"])
        # results.append(analysis)
       


    # with open('data/results-species.json', 'w') as RESULTS:
    #     RESULTS.write(json.dumps([r.items for r in results], indent=2))
    