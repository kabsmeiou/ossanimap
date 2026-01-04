def replace_spaces_and_dash_with_underscores(input_string: str) -> str:
    return input_string.replace(" ", "_").replace("-", "_")

# exclude spaces and underscores from removal
def remove_special_characters(input_string: str) -> str:
    return ''.join(e for e in input_string if e.isalnum() or e in [' ', '_'])