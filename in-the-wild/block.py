import click
import pprint

current_indentation = 0
indent_res = 4


def title(str):
    print("")
    click.secho(apply_indent(str))
    print("")

def say(str):
    click.secho(apply_indent(str))


def pretty(structure):
    formatted = pprint.pformat(structure, indent=indent_res * current_indentation)
    print("")
    click.secho(formatted)
    print("")

def remove_indent():
    global current_indentation
    current_indentation = 0

def indent(by=1):
    global current_indentation
    current_indentation = current_indentation + 1

def dedent(by=1):
    global current_indentation
    current_indentation = current_indentation - 1
    if current_indentation < 0:
        current_indentation = 0

def apply_indent(stri):
    indentation = (indent_res * current_indentation) * " "
    return indentation + stri



# nl=False