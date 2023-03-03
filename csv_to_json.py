import csv
import re

#https://stackoverflow.com/questions/7085512/check-what-number-a-string-ends-with-in-python
def get_trailing_number(s):
    m = re.search(r'\d+$', s)
    return int(m.group()) if m else None


if __name__ == "__main__":
    out_file = "output.json"
    string_builder = '{"contacts":['
    with open('./outputs/starlink-7/starlink_0 Contact Analysis.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        contact = 0
        for i, row in enumerate(reader):
            #Ignore the auto-generated header. Forgive me Father for this magic number.
            if i > 4:
                # Ignore delimiting rows
                if row[0] != 'Analysis' and row[0] != 'ID':
                    source_id = get_trailing_number(row[0].split(" - ")[0])
                    dest_id = get_trailing_number(row[0].split(" - ")[1])

                    #I put my thing down

                    string_builder += "{"
                    string_builder += '"contact": ' + str(contact) + ","
                    string_builder += '"source": ' +  str(source_id) + ","
                    string_builder += '"dest": ' + str(dest_id) + ","
                    string_builder += '"finalDestinationEid": "ipn:' + str(dest_id) + '.1",'
                    string_builder += '"start": ' + str(row[1]) + ","
                    string_builder += '"end": ' + str(row[2]) + ","
                    string_builder += '"rate": "1000"'
                    string_builder += "},"

                    #Flip it
                    contact += 1

                    #And Reverse It
                    string_builder += "{"
                    string_builder += '"contact": ' + str(contact) + ","
                    string_builder += '"source": ' +  str(dest_id) + ","
                    string_builder += '"dest": ' + str(source_id) + ","
                    string_builder += '"finalDestinationEid": "ipn:' + str(source_id) + '.1",'
                    string_builder += '"start": ' + str(row[1]) + ","
                    string_builder += '"end": ' + str(row[2]) + ","
                    string_builder += '"rate": "1000"'
                    string_builder += "},"

                    contact += 1
        string_builder = string_builder[:-1]
        string_builder += "]}"
    f = open(out_file, "w")
    f.write(string_builder)
    f.close()
