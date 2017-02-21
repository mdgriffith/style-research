
function getComputedStyles(node){
    var classes = node.className;
    if (classes == ""){ classes = null }

    var id = node.id;
    if (id == ""){ id = null }

    var nodeName = node.nodeName.toLowerCase();

    var style = window.getComputedStyle(node);
    var style_model = {};
    for (var j = style.length-1; j >= 0; j--) {
       var name = style[j];
       style_model[name] = style.getPropertyValue(name);
    }
    return { "style":style_model, "classes":classes, "id":id, "node":nodeName };
}

function childData(node, level){
    var data = []
    for (var i = 0; i < node.childElementCount; i++) {
        var child = node.children[i];
        var childLevel = level.slice();
        childLevel.push(i);
        var style = getComputedStyles(child);
        style["level"] = childLevel
        data.push(style);
        data = data.concat(childData(child, childLevel));
    }
    return data;
}



function httpGet(theUrl) {
    try {
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
        xmlHttp.send( null );
        return xmlHttp.responseText;
    } catch(err){
        console.log("err");
        console.log(err);
        return null;
    } 
}


function getStyleSheets(){
    var stylesheets = [];
    var styleSheetList = document.styleSheets;
    for (var i=0; i < document.styleSheets.length; i++){
        var styleSheet = document.styleSheets[i];
        // console.log(styleSheet);
        if (styleSheet.cssRules) {
            css = []
            for (var j=0; j < styleSheet.cssRules.length; j++){
                css.push(styleSheet.cssRules[j].cssText);
            }
            if (css.length > 0) {
                stylesheets.push(css.join("\n"));
            }
        } else if (styleSheet.href) {
            var newsheet = httpGet(styleSheet.href);
            if (newsheet != null) {
                stylesheets.push(newsheet);
            }
            
        }
    }
    return stylesheets.join("\n\n");
}

function getStylesheetNames(){
    var stylesheets = [];
    var styleSheetList = document.styleSheets;
    for (var i=0; i < document.styleSheets.length; i++){
        var styleSheet = document.styleSheets[i];
        // console.log(styleSheet);
        if (styleSheet.cssRules) {
            console.log("has rules, skipping");
        } else if (styleSheet.href) {
            stylesheets.push(styleSheet.href);
        }
    }
    return stylesheets;
}

function getInlineStyle(node){
    if (node.style != undefined){
        var inline_style = {};
        for (var j = node.style.length-1; j >= 0; j--) {
           var name = node.style[j];
           inline_style[name] = node.style.getPropertyValue(name);
        }
        return inline_style;
    }
    return {};
   
}


function just_path(obj){
    var new_obj = {};
    new_obj["classes"] = obj["classes"];
    new_obj["id"] = obj["id"];
    new_obj["node"] = obj["node"];
    return new_obj;
}

function getNodes(node, parents){
    if (parents == null || parents == undefined){
        parents = [];
    }

    var nodeName = node.nodeName.toLowerCase();
    if (nodeName == "#text"){return []}

    if (!'classList' in node) {
        return []
    }
    var classes = Array.from(node.classList.values());
    var id = node.id;
    if (id == ""){ id = null }


    var data = { "style": getInlineStyle(node)
               , "classes": classes
               , "id": id
               , "node": nodeName
               , "parents": parents
               }
    
    var children = []
    // check if the object has child nodes
    if (node.hasChildNodes()) {
        
        var childNodes = node.childNodes;

        for (var i = 0; i < childNodes.length; i++) {

            var new_parents = parents.slice();
            new_parents.push(just_path(data));
            children = children.concat(getNodes(childNodes[i], new_parents));
        }
    }
    data = [data];
    return data.concat(children);
}


var data = {}
var body = document.getElementsByTagName("body")[0];
var bodyStyle = getComputedStyles(body);
bodyStyle["level"] = [0];
var styles = [bodyStyle];
styles = styles.concat(childData(body, [0]));

data["computed_styles"] = styles
data["nodes"] = getNodes(document.getElementsByTagName("body")[0]);
data["stylesheet"] = getStyleSheets();

data["external_stylesheets"] = getStylesheetNames();

return data;