# v 2.0.2
import sys
import pymysql
import csv
from tabulate import tabulate
from slugify import slugify
import sqlparse
from datetime import datetime

def conn(host, user, password, database, port):
    try:
        data = [host, user, password, database, port]
        con = pymysql.connect(host=host,
                              user=user,
                              password=password,
                              database=database,
                              port=port,
                              charset='utf8mb4',
                              cursorclass=pymysql.cursors.DictCursor)
        # print("Connectie met de database is succesvol!")
        return con
    except ValueError as e:
        print(f"Error in database-connectie: {e}")
        print(f"Dit zijn de gegevens die je hebt verstuurd {data}")
        sys.exit(1)
    except Exception as e:
        print(f"Error:{e}")
        print(f"Dit zijn de gegevens die je hebt verstuurd {data}")
        sys.exit(1)
    


def cleardb(con, table):
    try:
        with con.cursor() as cur:
            sql = "DELETE FROM " + table
            cur.execute(sql)
            con.commit()
            notify = f"MySQL tabel { table } is leeggemaakt"
            print(notify)
    except pymysql.Error as e:
        print("Error %d: %s" % (e.args[0], e.args[1]))
        return False
    except:
        print("Tabel leegmaken is mislukt!")

def readfromdb(con, table):
    print(f"Reading from DB table {table}")
    sql = "select * from " + table
    try:
        with con.cursor() as cur:
            cur.execute(sql)
            con.commit()
            lines = []
            line = {}
            for rows in cur:
                for row in rows:
                    # print(row)
                    line[row] = str(rows[row])
                lines.append(line)
                line = {}
        return lines
    except pymysql.Error as e:
        print("Error %d: %s" % (e.args[0], e.args[1]))
        return False
    except:
        print("An error occured")


def create_csv(lines):
    print("Creating csv...")
    try:
        content = ";".join([str(i) for i in lines[0]]) + "\n"
        for line in lines:
            keys, values = zip(*line.items())
            content = content + ';'.join([str(i) for i in values]) + "\n"
        return content
    except IndexError as e:
        print(f"Error in create_csv: {e}")
    except:
        print("Error in create_csv")


def write_to_file(file, content):
    try:
        f = open(file, 'wt')
        f.write(content)
        f.close()

    except OSError as e:
        print('OSError, something with write_to_file', e)
    except IOError as ioe:
        print("IOError, something with write_to_file: ", ioe)
    except:
        print("write to file went wrong")

def append_to_file(file, content):
    try:
        f = open(file, 'at')
        if(type(content) == list):
            for line in content:
                f.write(line + "\n\n")
        else:
            f.write(content)
        f.close()

    except OSError as e:
        print('OSError, something with append_to_file', e)
    except IOError as ioe:
        print("IOError, something with append_to_file: ", ioe)
    except:
        print("appendto file went wrong")


def csv_to_dict(file):
    with open(file, mode='r') as infile:
        lines = csv.reader(infile)
        print(lines[0])


def csv_to_mysql(con, table, file):
    try:
        fields = ""
        cursor = con.cursor()
        csv_data = csv.reader(open(file), delimiter=';')
        for (i, row) in enumerate(csv_data, start=0):
            if i == 0:
                fields = ', '.join([(str(i)) for i in row])
                placeholders = ', '.join(['%s' for i in range(len(row))])
            else:
                sql = 'INSERT INTO ' + table + ' (' + fields + ')' + ' VALUES (' + placeholders + ')'
                cursor.execute(sql, row)
        con.commit()
        notify = f"Gegevens uit { file } zijn succesvol overgezet naar tabel { table }"
        print(notify)
    except FileNotFoundError as e:
        print("Error %d: %s" % (e.args[0], e.args[1]), file)
    except pymysql.Error as e:
        print("Error %d: %s" % (e.args[0], e.args[1]))
        return False
    except:
        print(f"records aan { table } toevoegen is mislukt")
        # cursor.close()


def select_query(con, sql, s):
    try:
         with con.cursor() as cur:
            cur.execute(sql)
            con.commit()
            header = []
            tabledata = []
            for row in cur.fetchall():
                data = []
                if len(header) == 0:
                    addheader = True
                else:
                    addheader = False
                for key, value in row.items():
                    if addheader:
                        header.append(key)
                    data.append(value)
                if addheader:
                    tabledata.append(header)
                tabledata.append(data)
            output = tabulate(tabledata, headers='firstrow') + "\n"
            return output
    except pymysql.Error as e:
        print("Error %d: %s" % (e.args[0], e.args[1]))
        return False
    except:
        print("select_query went wrong")


def outputToFile(question, sql, s, output):
    myfile = student_file(s)
    separator = 80 * "="
    tofile = [
         "***Datum:***  " + datetime.now().strftime('%d-%m-%Y, %H:%M:%S'),
         "***Student:***  \n" + student(s),
         "***Vraag:***  \n" + question,
         "***Query:***  \n```sql\n" + sqlparse.format(sql, reindent=True, keyword_case='upper') + "\n```",
         "***Output:***\n```csv\n" + str(output) + "\n```",
    ]

    append_to_file(myfile, tofile)

def outputToScreen(output, s):
    print("\n" + student(s) + "\n")
    print(output)


def student(dict):
    return " | ".join("{}: {}".format(k, v) for k, v in dict.items())



def student_file(dict):
    return slugify(f"{dict['Studentnummer']}-{dict['Naam']}") + ".md"


def question(questions, keuze, s):
    question = [q for i, q in enumerate(questions, start=1) if i == keuze][0]
    append_to_file(student_file(s), student(s) +"\n\n")
    append_to_file(student_file(s), question +"\n")

def clear_database(con, tables, s):
    print("clearing database...")
    # clear textfile student
    write_to_file(student_file(s), "")
    print(f"{student_file(s)} is leeggemaakt")
    # tabelvolgorde omdraaien ivm contstraints
    tables.reverse()
    for table in tables:
        cleardb(con, table)
    # tabelvolgorde herstellen
    tables.reverse()


def setup_database(con, env):
    for table in  env["tables"]:
        filename = env["path"] + table + ".csv"
        csv_to_mysql(con, table, filename)


def setup_csv_files(con, env):
    for table in env["tables"]:
        filename = env["path"] + table + ".csv"
        lines = readfromdb(con, table)
        content = create_csv(lines)
        write_to_file(filename, content)