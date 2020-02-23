operators = ('+' , '-' , '*' , '/' , '**' , ')' , '(')

def separateMessage(message: str)-> list:
    '''Get str expressin and separate him'''
    # if message have float or simple ','/'.'
    if message.find('.') != -1 or message.find(',') != -1:
        #raise
        return
    new_message = []
    row = str()
    for x in message:
        # Operators work how separator
        if x in operators:
             new_message.append(row.rstrip())
             new_message.append(x)
             row = str()
        else:
            row += x
    new_message.append(row)
    return new_message
