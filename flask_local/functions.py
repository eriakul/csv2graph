#may need to pip install pygal

#Functions needed:
#Processes possible variables
#Creates dictionary out of variables
#Creates title
#Creates axes



import csv
import string
from bokeh.plotting import figure, output_file, show

def open_file_as_rows(file_name):
    try:
        with open(file_name, 'r') as f:
            rows_csv = csv.reader(f, dialect='excel')
            rows = []
            for row in rows_csv:
                    rows.append(row)
        return rows
    except:
        print("Could not find the file. Make sure it is in the correct directory and try again.\n")
        quit()

def is_number(string):
    try:
        float(string)
    except ValueError:
        return False
    return True

def is_text(string):
    if is_number(string) or string.replace(" ", "") == "":
        return False
    return True

def is_yes(string):
    string = string.lower()
    string = string.replace(" ", "")
    while not string in ['yes', 'no']:
        string = input('Please type "yes" or "no".')
    if string == 'yes':
        return True
    elif string == 'no':
        return False

def remove_title_row(rows):
    cut_off = 50
    if cut_off > len(rows[0]):
        cut_off = len(rows[0]) - 1
    done = False
    while done == False:
        done = True
        for index in range(1,cut_off):
            if len([1 for i in rows[index] if is_text(i)]) > len([1 for i in rows[0] if is_text(i)]):
                done = False
        if done == False:
            possible_title = ''.join([i+" " for i in rows[0]]).strip(" ")
            print('"'+possible_title+'"\n\n'+"Are these variables you want to plot? (yes/no)")
            yes_or_no = 'no'
            if not is_yes(yes_or_no):
                print("\nRemoving unnecessary row...\n")
                rows = rows[1:]
            else:
                return rows
    return rows

def rows_to_columns(rows, list_of_column_indexes):
    list_of_columns = []
    for i in list_of_column_indexes:
        column = []
        for j in range(len(rows)):
            column.append(rows[j][i])
        list_of_columns.append(column)
    return list_of_columns

def delete_columns_with_less_than_threshold_numbers_and_turn_to_columns(rows, threshold):
    threshold = len(rows)*threshold
    valid_columns = []
    for i in range(len(rows[0])):
        number_of_digits = 0
        for j in range(len(rows)):
            item = rows[j][i]
            if is_number(item):
                number_of_digits += 1
        if number_of_digits > threshold:
            valid_columns.append(i)
    return rows_to_columns(rows, valid_columns)

def return_dictionary_of_variables_and_lists(columns):
    #finds first column of all number
    for i in range(len(columns[0])):
        if len([1 for j in range(len(columns)) if not is_number(columns[j][i])]) == 0:
            index_of_start = i
            break
    #runs making variable name code up until that
    dictionary = {}
    for column in columns:
        variable_name = ''
        for j in range(index_of_start):
            if is_text(column[j]):
                variable_name = variable_name+column[j]+" "
        variable_name = variable_name.strip(" ")
        if len(variable_name)>40:
            variable_name = variable_name[:15] + "..." +variable_name[-7:]
        #makes list of number values after where non numbers become none
        dictionary[variable_name] = []
        for j in range(index_of_start, len(column)):
            if is_number(column[j]):
                dictionary[variable_name].append(float(column[j]))
            else:
                dictionary[variable_name].append(float('NaN'))
    return dictionary

def open_file_into_dictionary(file_name):
    rows = open_file_as_rows(file_name)
    rows = remove_title_row(rows)
    columns = delete_columns_with_less_than_threshold_numbers_and_turn_to_columns(rows, .8)
    return return_dictionary_of_variables_and_lists(columns)

def print_variables_found_on_file(keys):
    counter = 0
    print("Variables found in file: \n")
    for variable in keys:
        print(str(counter+1) + ". " + variable)
        counter += 1


def get_variables_to_plot(dictionary):
    """Returns list where first element is x_axis and
    subsequent elements are y_axis."""
    done = False
    keys = list(dictionary.keys())
    print_variables_found_on_file(keys)
    print("\n\nWhich variable is the x-axis? (Give the number.)")
    x_axis = [keys[int(input()) - 1]]
    y_axis = []
    while not done:
        print_variables_found_on_file(keys)
        print("\n\nWhich variable is the y-axis? (Give the number.)")
        y_axis.append(keys[int(input()) - 1])
        print("\nX-axis: " + x_axis[0] + "\nY-axis: "+
        "".join([i+", " for i in y_axis]).strip(", "))
        done = not is_yes(input("\nAdd more y-axis values?\n"))
    return x_axis+y_axis











if __name__ == "__main__":
    pass
