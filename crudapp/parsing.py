
# functions that help in parsing db responses

#format response by taking advantage of fact response is tuples
def format_response(field_names, tuple):
        response=dict()
        if len(field_names) > len(tuple):
                raise Exception("Expected fields missing or not all mapped.")

        for i in range(0, len(field_names)):
                #if condition allows for values to be overidden, if new value isnt null
                if field_names[i] in response and tuple[i] is None:
                        continue

                response[field_names[i]] = tuple[i]

        return response


#format a list of responses
def format_all_responses(field_names, array):
        response = list()
        for i in range(0, len(array)):
                o = format_response(field_names, array[i])
                response.append(o)

        return response

#have to do both of these at the same time because keys could be accessed in different orders
def organize_col_names(map):
        col_names=""
        format_names=""
        for key in map:
                col_names += key+","
                format_names += "%("+key+")s,"
        col_names = col_names[0:len(col_names)-1]
        format_names = format_names[0:len(format_names)-1]
        return col_names,format_names


