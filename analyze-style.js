





function match(obj1, obj2){
    for (var key in obj1) {
        if (obj1.hasOwnProperty(key)) {
            if (obj2.hasOwnProperty(key)){
                if (obj1[key] != obj2[key]){
                    return false;
                } 
            } else { return false }
        }
    }
    return true;
}


color_fields = ["color", "background-color", "border-color"]
color_species = []
unique_colors = []

function count_color_model(color_model){


    // Count colors
    for (var key in color_model) {
        if (color_model.hasOwnProperty(key)) {
            color_model[key] = color_model[key].substring(4, color_model[key].length-1)
                                             .replace(/[rgba\(\)\s]/g, '')
                                             .split(',');

            if (color_model[key].length == 3) { color_model[key].push(1) } // add alpha if not present
            var channels = color_model[key].length;
            for (var w = 0; w < channels; w++) {
               color_model[key][w] = parseFloat(color_model[key][w]);
            }

            color_model[key] = color_model[key].join(",")

        }
    }


    // Count species
    var color_count = color_species.length;
    var counted = false;
    for (var i = 0; i < color_count; i++) {
        if (match(color_species[i]["model"], color_model) ){
            color_species[i]["count"] = color_species[i]["count"] + 1
            counted = true;
            break;
        }
    }
    if (!counted){
        color_species.push({"model": color_model, "count": 1})
    }


    // Count colors
    for (var key in color_model) {
        if (color_model.hasOwnProperty(key)) {
            if (unique_colors.indexOf(color_model[key]) < 0) {
                unique_colors.push(color_model[key]);
            }
        }
    }
}


font_fields = ["font-size", "font-family", "text-align", "line-height"]
font_species = []
unique_sizes = []






function count_font_model(font_model){

    // Count species
    var font_count = font_species.length;
    var counted = false;
    for (var i = 0; i < font_count; i++) {
        if (match(font_species[i]["model"], font_model) ){
            font_species[i]["count"] = font_species[i]["count"] + 1
            counted = true;
            break;
        }
    }
    if (!counted){
        font_species.push({"model": font_model, "count": 1})
    }


    // Count sizes
    if ('font-size' in font_model) {
        if (unique_sizes.indexOf(font_model['font-size']) < 0) {
              unique_sizes.push(font_model['font-size']);
        }
    }
}



    


var elements = document.querySelectorAll("*");
var elementCount = elements.length;
for (var i = 0; i < elementCount; i++) {

    var style = window.getComputedStyle(elements[i]);

    var color_model = {}
    var font_model = {}
    for (var j = style.length-1; j >= 0; j--) {
       var name = style[j];
       if (color_fields.indexOf(name) > -1) {
           var val = style.getPropertyValue(name);
           color_model[name] = val;
       }

       if (font_fields.indexOf(name) > -1) {
           var val = style.getPropertyValue(name);
           font_model[name] = val;
       }

    }

    count_color_model(color_model)
    count_font_model(font_model)
    // if (i >  1){ break; }
}

function just_values(model) {
    values = []
    for (var i = 0; i < model.length; i++) {
      values.push(model[i]["model"]);
    }
    return values;
}


// font_fields = ["font-size", "font-family", "text-align", "line-height"]

function breakdown(model) {
    counts = {}
    for (var i = 0; i < model.length; i++) {
        for (var key in model[i]) {
            if (model[i].hasOwnProperty(key)) {
               
                if (model[i][key] in counts) {
                  counts[model[i][key]] = counts[model[i][key]] + 1
                } else {
                  counts[model[i][key]] = 1
                }
                

            }
        }

    }
    return counts;
}


console.log("COLORS");
console.log(breakdown(just_values(color_species)));
console.log(color_species.length);
console.log(unique_colors);
console.log(unique_colors.length);


console.log("FONTS");
console.log(breakdown(just_values(font_species)));
console.log(font_species.length);
console.log(unique_sizes);
console.log(unique_sizes.length)