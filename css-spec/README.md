# CSS Spec


Types of questions we want to ask:

  * What properties deal with color
  * What properties handle font
  * What properties disable or modify other properties (search for text that says "ignore, depending on, etc.")
    * Exception for shorthand properties
  * Property Compatibility
    * What prefixes are required?



Data sketch

```json
// Properties
{ "name": "display"
, "type": "property"
, "url": "url/to/reference"
, "values":
   
}

// Shorthand
{ "name": "background"
, "type": "shorthand"
, "url": "url/to/reference"
, "shorthand_for":
    [ "background-image"
    , "background-position"
    , "background-size"
    ]
}

// Values
{ "name": "display_values"
, "values":
    [ "static"
    , "relative"
    , "absolute"
    ]
}





```