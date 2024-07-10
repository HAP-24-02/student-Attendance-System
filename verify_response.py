def reorder_response(response):
    name = None
    roll_number = None
    
    for value in response:
        if any(char.isdigit() for char in value):
            roll_number = value
        else:
            name = value
    
    return [name, roll_number]
