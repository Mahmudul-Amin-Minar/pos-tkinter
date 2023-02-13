import os
import sqlite3
from tkinter import *
from tkinter import messagebox

root = Tk()
root.iconbitmap('../icon/fox.ico')
root.title("Customer")
# root.geometry("1280x720")


if not os.path.exists('address_book.db'):
    # create a database or connect to one 
    conn = sqlite3.connect('address_book.db')
    # create cursor 
    c = conn.cursor()
    # insert into database


    # create table 
    c.execute("""
        create table addresses(
            first_name text,
            last_name text,
            address text,
            city text,
            zipcode integer
        )
    """)
    # commit 
    conn.commit()
    # close the connection
    conn.close()

# create submit function 
def submit():
    # create a database or connect to one 
    conn = sqlite3.connect('address_book.db')
    # create cursor 
    c = conn.cursor()
    # insert into database
    c.execute("INSERT INTO addresses VALUES (:f_name, :l_name, :address, :city, :zip_code)", 
        {
            'f_name': f_name.get(),
            'l_name': l_name.get(),
            'address': address.get(),
            'city': city.get(),
            'zip_code': zip_code.get()
        }
    )

    # commit 
    conn.commit()
    # close the connection
    conn.close()


    # clear the text boxes 
    f_name.delete(0, END)
    l_name.delete(0, END)
    address.delete(0, END)
    city.delete(0, END)
    zip_code.delete(0, END)


def query():
    # create a database or connect to one 
    conn = sqlite3.connect('address_book.db')
    # create cursor 
    c = conn.cursor()

    # query the database 
    c.execute("SELECT *, oid FROM addresses")
    records = c.fetchall()
    print(records)
    print_records = ""
    for record in records:
        print_records += str(record) + "\n"
    query_label = Label(root, text=print_records)
    query_label.grid(row=8, column=0, columnspan=2)

    # commit 
    conn.commit()
    # close the connection
    conn.close()
    

# create text boxes
f_name = Entry(root, width=30)
f_name.grid(row=0, column=1, padx=20)

l_name = Entry(root, width=30)
l_name.grid(row=1, column=1, padx=20)

address = Entry(root, width=30)
address.grid(row=2, column=1, padx=20)

city = Entry(root, width=30)
city.grid(row=3, column=1, padx=20)

zip_code = Entry(root, width=30)
zip_code.grid(row=4, column=1, padx=20)

# create text box labels 
f_name_label = Label(root, text="First Name")
f_name_label.grid(row=0, column=0)

l_name_label = Label(root, text="Last Name")
l_name_label.grid(row=1, column=0)

address_label = Label(root, text="Address Name")
address_label.grid(row=2, column=0)

city_label = Label(root, text="City Name")
city_label.grid(row=3, column=0)

zip_label = Label(root, text="Zip code")
zip_label.grid(row=4, column=0)

# create submit button 
submit_button = Button(root, text="Add record to database", command=submit)
submit_button.grid(row=6, column=0, columnspan=2, pady=10, padx=10, ipadx=100)

# create a query button 
query_btn = Button(root, text="Show records", command=query)
query_btn.grid(row=7, column=0, columnspan=2, pady=10, padx=10, ipadx=137)



root.mainloop()