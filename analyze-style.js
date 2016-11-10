
function getStyles(node){
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
        var style = getStyles(child);
        style["level"] = childLevel
        data.push(style);
        data = data.concat(childData(child, childLevel));
    }
    return data;
}

var body = document.getElementsByTagName("body")[0];
var bodyStyle = getStyles(body);
bodyStyle["level"] = [0];
var styles = [bodyStyle];
styles = styles.concat(childData(body, [0]));

return styles;