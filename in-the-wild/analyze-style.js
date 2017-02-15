
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
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
    xmlHttp.send( null );
    return xmlHttp.responseText;
}


function getStyleSheets(){
    var stylesheets = {}
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
                stylesheets[i] = css.join("\n")
            }
        } else if (styleSheet.href) {
            stylesheets[i] = httpGet(styleSheet.href);
        }
    }
    return stylesheets;
}

var data = {}






var body = document.getElementsByTagName("body")[0];
var bodyStyle = getComputedStyles(body);
bodyStyle["level"] = [0];
var styles = [bodyStyle];
styles = styles.concat(childData(body, [0]));

data["computed_styles"] = styles
data["stylesheets"] = getStyleSheets();

return styles;