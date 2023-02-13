import csv
import datetime as dt
import os
import sqlite3
import subprocess
from datetime import date, datetime
from tkinter import *

import jinja2
import pdfkit
import xlsxwriter

path = os.getcwd()
parent_directory = os.path.abspath(os.path.join(path, os.pardir))

root = Tk()
root.iconbitmap('../icon/icon.jpg')
root.title("BigganBaksho POS")
root.geometry("1280x720")

SUB_TOTAL = 0
DISCOUNT = 0
PAYABLE_AMOUNT = 0
CASH_RECEIVED = 0
CASH_RETURN = 0
DISCOUNT_STR = '0'

today = date.today()

if not os.path.exists('../db/orders.db'):
    # create a database or connect to one 
    conn = sqlite3.connect('../db/orders.db')
    # create cursor 
    c = conn.cursor()
    # create table 
    c.execute("""
        CREATE TABLE orders(
            customer_name TEXT,
            customer_phone TEXT,
            quantity INTEGER,
            subtotal INTEGER,
            discount INTEGER,
            gift TEXT,
            cash_received INTEGER,
            cash_return INTEGER,
            date TEXT,
            time TEXT,
            product_ids TEXT,
            product_names TEXT
        )
    """)
    # commit 
    conn.commit()
    # close the connection
    conn.close()

if not os.path.exists('../db/products.db'):
    # create a database or connect to one 
    conn = sqlite3.connect('../db/products.db')
    # create cursor 
    c = conn.cursor()
    # create table 
    c.execute("""
        create table products(
            product_id text,
            barcode_id text,
            unit_price integer
        )
    """)
    products = [("12001 - ONNOROKOM BIGGANBAKSHO (ALOR JHALAK)",	"10000001",	925),
        ("12021 - ONNOROKOM SCIENCE BOX (COLOR OF LIGHT)",	"40000001",	990),
        ("12002 - ONNOROKOM BIGGANBAKSHO (CHUMBAKAR CHAMAK)",   "20000001",	990),
        ("12022 - ONNOROKOM SCIENCE BOX (MAGIC OF MAGNET)",	"50000001",	1150),
        ("12003 - ONNOROKOM BIGGANBAKSHO (TARIT TANDOB)",	"30000001",	975),
        ("12023 - ONNOROKOM SCIENCE BOX (AMAZING ELECTRICITY)",	"60000001",	1100),
        ("12004 - ONNOROKOM BIGGANBAKSHO (RASHAYON RAHASSHO)",	"70000001",	995),
        ("12024 - ONNOROKOM SCIENCE BOX (MYSTERY OF CHEMISTRY)",	"90000001",	1200),
        ("12005 - ONNOROKOM BIGGANBAKSHO (ODVUT MAPJOKH)",	"80000001",	980),
        ("12025 - ONNOROKOM SCIENCE BOX (FUN WITH MEASUREMENT)",	"11000001",	1050),
        ("12006 - ONNOROKOM BIGGANBAKSHO (SHOBDO KALPO)",	"12000001",	1990),
        ("12026 - ONNOROKOM SCIENCE BOX (SOUND BOUND)",	"13000001",	2120),
        ("12012 - MAJAR PERISCOPE",	"14000001",	295),
        ("12013 - GIANT PIXEL",	"15000001",	880),
        ("12007 - SMART KIT (FOCUS CHALLENGE, BANGLA VERSION)",	"17000001",	880),
        ("12027 - SMART KIT (FOCUS CHALLENGE, ENGLISH VERSION)",	"18000001",	880),
        ("12015 - ONNOROKOM BIGGANBAKSHO (CLASS FIVE KIT)",	"16000001",	2990),
        ("12014 - ONNOROKOM BIGGANBAKSHO (TAN-GRAM)",	"19000001",	480),
        ("12016 - SMART KIT (CAPTAIN CURIOUS)",	"21000001",	590)
    ]

    c.executemany('INSERT INTO products VALUES(?,?,?)', products)
    # commit 
    conn.commit()
    # close the connection
    conn.close()

def searchProduct(id):
    conn = sqlite3.connect('../db/products.db')
    # create cursor 
    c = conn.cursor()
    
    lookup_id = id[:2]

    c.execute("SELECT * FROM products WHERE barcode_id like ?", (lookup_id+'%',))
    record = c.fetchall()
    # print(record)
    # close the connection
    conn.close()
    return record

def remove_item(items, item):
 
    # remove the item for all its occurrences
    c = items.count(item)
    for _ in range(c):
        items.remove(item)
 
    return items

def giftCalculate():
    global SUB_TOTAL, DISCOUNT, PAYABLE_AMOUNT, DISCOUNT_STR
    DISCOUNT = 0
    DISCOUNT_STR = '0'

    items = []
    items_buy = 0

    for i in treeview_items.get_children():
        item_id = str(treeview_items.item(i)['values'][3])[:2]
        items.append(item_id)
        # items_buy += treeview_items.item(i)['values'][1]
        # print(treeview_items.item(i))
        # print(items_buy)
    print(items)
    if '16' in items:
        c = items.count('16')
        five_kit_dis = 300*c
        DISCOUNT +=  five_kit_dis
        if DISCOUNT_STR.find("gift") != -1:
            DISCOUNT_STR = str(DISCOUNT) + "+gift"
        else:
            DISCOUNT_STR = str(DISCOUNT)
        items = remove_item(items, '16')

    if '14' in items:
        items = remove_item(items, '14')

    if '19' in items:
        items = remove_item(items, '19')
    
    print(items)
    items_buy = len(items)

    if items_buy == 2 and '14' not in items and '19' not in items:
        DISCOUNT += 150
        DISCOUNT_STR = str(DISCOUNT)
    if items_buy == 3 and '14' not in items and '19' not in items:
        DISCOUNT += 150
        DISCOUNT_STR = str(DISCOUNT) + '+gift'
    # if items_buy == 4 and '14' not in items and '19' not in items:
    #     print(4)
    #     DISCOUNT += 150+150
    #     DISCOUNT_STR = str(DISCOUNT)
    # if items_buy == 5 and '14' not in items and '19' not in items:
    #     DISCOUNT += 150+150
    #     DISCOUNT_STR = str(DISCOUNT) + '+gift'
    if items_buy == 6:
        DISCOUNT += 500
        DISCOUNT_STR = str(DISCOUNT) + '+watch'
        

    discount_amount.delete(0, END)

    PAYABLE_AMOUNT = SUB_TOTAL - DISCOUNT

    discount_amount.insert(0, DISCOUNT_STR)
    payable_amount.insert(0, PAYABLE_AMOUNT)
    

def proceedOrdering():
    global SUB_TOTAL, DISCOUNT, PAYABLE_AMOUNT, DISCOUNT_STR, CASH_RECEIVED, CASH_RETURN
    CASH_RECEIVED = 0
    CASH_RETURN = 0
    
    CASH_RECEIVED = int(cash_received_amount.get())
    if CASH_RECEIVED >= PAYABLE_AMOUNT:
        CASH_RETURN = CASH_RECEIVED - PAYABLE_AMOUNT
        cash_return_amount.insert(0, CASH_RETURN)


def clearOrderDetails():
    sub_total_amount.delete(0, END)
    discount_amount.delete(0, END)
    payable_amount.delete(0, END)
    total_price.delete(0, END)


def addProduct():

    clearOrderDetails()

    p_id = product_id.get()
    record = searchProduct(p_id)
    p_name = record[0][0]
    p_price = record[0][2]
    product_unit_price.insert(0, p_price)
    qty.insert(0, 1)
    quantity = qty.get()
    barcode_id = product_id.get()
    total_amount = int(p_price) * int(quantity)

    global SUB_TOTAL, DISCOUNT, PAYABLE_AMOUNT
    SUB_TOTAL += total_amount
    sub_total_amount.insert(0, SUB_TOTAL)
    
    treeview_items.insert(parent="", index=0, text=str(p_name), values=(str(p_price), str(quantity), str(total_amount), barcode_id))
    update_count()

    total_price.insert(0, total_amount)

    product_id.delete(0, END)
    product_unit_price.delete(0, END)
    qty.delete(0, END)


def fill_q_price():
    pass

def update_count():
    count.delete(0, END)
    count.insert(0, len(treeview_items.get_children()))


def deleteOne():
    x = treeview_items.selection()[0]
    item = treeview_items.item(x)

    quantity = item['values'][1]
    total_amount = int(item['values'][0]) * int(quantity)
    global SUB_TOTAL, DISCOUNT, PAYABLE_AMOUNT
    SUB_TOTAL -= total_amount
    # DISCOUNT -= DISCOUNT
    # PAYABLE_AMOUNT = SUB_TOTAL - DISCOUNT

    clearOrderDetails()

    sub_total_amount.insert(0, SUB_TOTAL)
    # discount_amount.insert(0, DISCOUNT)
    # payable_amount.insert(0, PAYABLE_AMOUNT)
    treeview_items.delete(x)
    update_count()
    giftCalculate()

def clearForm():
    product_id.delete(0, END)
    product_unit_price.delete(0, END)
    qty.delete(0, END)

    customer_name.delete(0, END)
    customer_phone.delete(0, END)

    sub_total_amount.delete(0, END)
    discount_amount.delete(0, END)
    payable_amount.delete(0, END)
    cash_received_amount.delete(0, END)
    cash_return_amount.delete(0, END)
    global SUB_TOTAL, DISCOUNT, PAYABLE_AMOUNT, DISCOUNT_STR

    SUB_TOTAL = 0
    DISCOUNT = 0
    PAYABLE_AMOUNT = 0
    CASH_RECEIVED = 0
    CASH_RETURN = 0
    DISCOUNT_STR = '0'
    treeview_items.delete(*treeview_items.get_children())

def clearProductForm():
    product_id.delete(0, END)
    product_unit_price.delete(0, END)
    qty.delete(0, END)
    total_price.delete(0, END)


def printVoucher():
    if CASH_RECEIVED >= PAYABLE_AMOUNT:
        cust_name = str(customer_name.get())
        cust_phone = str(customer_phone.get())
        global today
        str_today = str(today)
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_time = str(current_time)

        conn = sqlite3.connect('../db/orders.db')
        # create cursor 
        c = conn.cursor()

        gift = ''
        print(DISCOUNT_STR)
        if DISCOUNT_STR.find('+') != -1:
            gift = DISCOUNT_STR.split('+')[1]
        else:
            gift = gift

        order_details = {
            "customer_name": cust_name,
            "customer_phone": cust_phone,
            "today": str_today,
            "current_time": current_time,
            "subtotal": format(SUB_TOTAL, ',d'),
            "discount": format(DISCOUNT, ',d'),
            "gift": gift,
            "payable_amount": format(PAYABLE_AMOUNT, ',d'),
            "cash_received": format(CASH_RECEIVED, ',d'),
            "cash_return": format(CASH_RETURN, ',d')
        }

        other_products = [("ONNOROKOM BIGGANBAKSHO (ALOR JHALAK)[BDT 925]"),
            ("ONNOROKOM SCIENCE BOX (COLOR OF LIGHT)[BDT 990]"),
            ("ONNOROKOM BIGGANBAKSHO (CHUMBAKAR CHAMAK)[BDT 990]"),
            ("ONNOROKOM SCIENCE BOX (MAGIC OF MAGNET)[BDT 1150]"),
            ("ONNOROKOM BIGGANBAKSHO (TARIT TANDOB)[BDT 975]"),
            ("ONNOROKOM SCIENCE BOX (AMAZING ELECTRICITY)[BDT 1100]"),
            ("ONNOROKOM BIGGANBAKSHO (RASHAYON RAHASSHO)[BDT 995]"),
            ("ONNOROKOM SCIENCE BOX (MYSTERY OF CHEMISTRY)[BDT 1200]"),
            ("ONNOROKOM BIGGANBAKSHO (ODVUT MAPJOKH)[BDT 980]"),
            ("ONNOROKOM SCIENCE BOX (FUN WITH MEASUREMENT)[BDT 1050]"),
            ("ONNOROKOM BIGGANBAKSHO (SHOBDO KALPO)[BDT 1990]"),
            ("ONNOROKOM SCIENCE BOX (SOUND BOUND)[BDT 2120]"),
            ("MAJAR PERISCOPE[BDT 295]"),
            ("GIANT PIXEL[BDT 880]"),
            ("SMART KIT (FOCUS CHALLENGE, BANGLA VERSION)[BDT 880]"),
            ("SMART KIT (FOCUS CHALLENGE, ENGLISH VERSION)[BDT 880]"),
            ("ONNOROKOM BIGGANBAKSHO (CLASS FIVE KIT)[BDT 2990]"),
            ("ONNOROKOM BIGGANBAKSHO (TAN-GRAM)[BDT 480]"),
            ("SMART KIT (CAPTAIN CURIOUS)[BDT 590]")]

        products = []
        product_ids = []
        product_names = []
        for index,i in enumerate(treeview_items.get_children()):
            # print(treeview_items.item(i))
            x = treeview_items.item(i)
            sl_no = index+1
            product_name = x['text']
            quantity = x['values'][1]
            unit_price = x['values'][0]
            price = x['values'][2]
            unique_id = x['values'][3]
            to_be_removed = product_name.split('-')[1].strip()+"[BDT "+str(unit_price)+"]"
            print(to_be_removed)
            try:
                other_products.remove(to_be_removed)
            except:
                pass

            product = {
                "sl_no": sl_no,
                "product_name": product_name.split('-')[1],
                "quantity": quantity,
                "unit_price": unit_price,
                "price": price,
                "unique_id": unique_id,
            }
            product_ids.append(unique_id)
            product_names.append(product_name)
            products.append(product)
        print(products)
        # print(other_products)
        print(order_details)

        pdf_make(products, order_details, other_products)

        c.execute("INSERT INTO orders VALUES (:customer_name, :customer_phone, :quantity, :subtotal, :discount, :gift, :cash_received, :cash_return, :date, :time, :product_ids, :product_names)", 
            {
                'customer_name': cust_name,
                'customer_phone': cust_phone,
                'quantity': len(products),
                'subtotal': SUB_TOTAL,
                'discount': DISCOUNT,
                'gift': gift,
                'cash_received': CASH_RECEIVED,
                'cash_return': CASH_RETURN,
                'date': str_today,
                'time': current_time,
                'product_ids': str(product_ids),
                'product_names': str(product_names)
            }
        )
        # record = c.fetchall()
        # print(record)
        # close the connection
        conn.commit()
        conn.close()
        clearForm()
        todays_sale()
        one_month_sale()
    else:
        pass


def pdf_make(products, order_details, other_products):
    context = {
        'products': products,
        'order_details': order_details,
        'other_products': other_products
    }
    template_loader = jinja2.FileSystemLoader('../template/')
    template_env = jinja2.Environment(loader=template_loader)

    html_template = 'template.html'
    template = template_env.get_template(html_template)
    output_text = template.render(context)

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
    output_pdf = '../template/pdf_generated.pdf'
    pdfkit.from_string(output_text, output_pdf, configuration=config, options={"enable-local-file-access": ""}, css='../template//style.css')

    open_pdf()


def open_pdf():
    path = parent_directory + '/template/pdf_generated.pdf'
    subprocess.Popen([path], shell=True)

def todays_sale():
    conn = sqlite3.connect('../db/orders.db')
    # create cursor 
    c = conn.cursor()
    lookup_date = str(today)

    c.execute("SELECT * FROM orders WHERE date=?", (lookup_date,))
    records = c.fetchall()
    # close the connection
    conn.close()

    path = parent_directory+'/reports'
    # making csv file 
    header = ["customer_name", "customer_phone", "quantity", "subtotal", "discount", "gift", "cash_received", "cash_return", "date", "time", "product_ids", "product_names"]

    
    workbook = xlsxwriter.Workbook(path+'/todays_sale.xlsx')
    xl_path = path+'/todays_sale.xlsx'
    worksheet = workbook.add_worksheet()
    row = 0
    column = 0
    for item in header :
        worksheet.write(row, column, item)
        column += 1
    
    row = 1
    column = 0

    for item in records :
        column = 0
        for cell_item in item:
            worksheet.write(row, column, cell_item)
            column += 1
        row += 1
    
    workbook.close()
    # subprocess.Popen([xl_path], shell=True)

def one_month_sale():
    conn = sqlite3.connect('../db/orders.db')
    # create cursor 
    c = conn.cursor()
    lookup_date_begin = today - dt.timedelta(days=30)
    lookup_date_begin = str(lookup_date_begin)
    lookup_date_end = str(today)

    c.execute("SELECT * FROM orders WHERE date between ? and ?", (lookup_date_begin, lookup_date_end))
    records = c.fetchall()
    # close the connection
    conn.close()

    path = parent_directory + '/reports'
    # making csv file 
    header = ["customer_name", "customer_phone", "quantity", "subtotal", "discount", "gift", "cash_received", "cash_return", "date", "time", "product_ids", "product_names"]

    workbook = xlsxwriter.Workbook(path+'/one_months_sale.xlsx')
    xl_path = path+'/one_months_sale.xlsx'
    worksheet = workbook.add_worksheet()
    row = 0
    column = 0
    for item in header :
        worksheet.write(row, column, item)
        column += 1
    
    row = 1
    column = 0

    for item in records :
        column = 0
        for cell_item in item:
            worksheet.write(row, column, cell_item)
            column += 1
        row += 1
    
    workbook.close()
    # subprocess.Popen([xl_path], shell=True)


# create frame for customer details 
cust_frame = LabelFrame(root, text="Customer Details", padx=5, pady=20)

# create text box labels and input boxes for customer
customer_name_label = Label(cust_frame, text="Customer Name")
customer_name_label.grid(row=0, column=0)
customer_name = Entry(cust_frame, width=51)
customer_name.grid(row=0, column=1)

customer_phone_label = Label(cust_frame, text="Customer Phone")
customer_phone_label.grid(row=0, column=2)
customer_phone = Entry(cust_frame, width=31)
customer_phone.grid(row=0, column=3)

date_label = Label(cust_frame, text="Date")
date_label.grid(row=0, column=4)
date_f = Entry(cust_frame, width=22)
date_f.grid(row=0, column=5)

cust_frame.grid(row=0, column=0, padx=5)


date_f.insert(0, today)
date_f.config(state=DISABLED)

# create frame for product details 
prod_frame = LabelFrame(root, text="Product Details", padx=5, pady=20)

# create text box labels and input boxes for product
product_id_label = Label(prod_frame, text="Product ID")
product_id_label.grid(row=0, column=0)
product_id = Entry(prod_frame, width=30)
product_id.grid(row=0, column=1)

product_unit_price_label = Label(prod_frame, text="Unit Price")
product_unit_price_label.grid(row=0, column=2)
product_unit_price = Entry(prod_frame, width=30, bg='#C5C6D0')
product_unit_price.grid(row=0, column=3)

qty_label = Label(prod_frame, text="Qty")
qty_label.grid(row=0, column=4)
qty = Entry(prod_frame, bg='#C5C6D0')
qty.grid(row=0, column=5)

total_price_label = Label(prod_frame, text="Total Price")
total_price_label.grid(row=0, column=6)
total_price = Entry(prod_frame, bg='#C5C6D0')
total_price.grid(row=0, column=7)

# add_btn = Button(prod_frame, command=addProduct, text="Add", padx=20, bg="green", fg="white")
add_btn = Button(prod_frame, command=lambda:[addProduct(), giftCalculate()], text="Add", padx=20, bg="green", fg="white")
add_btn.grid(row=2, column=6, pady=10)
clear_btn = Button(prod_frame, command=clearProductForm, text="Clear", padx=20, bg="orange", fg="white")
clear_btn.grid(row=2, column=7, pady=10)

prod_frame.grid(row=1, column=0, padx=5)


# create frame for product cart 
cart_frame = LabelFrame(root, text="Cart", padx=0, pady=0)

import tkinter as tk
from tkinter import ttk

style = ttk.Style()
style.theme_use('clam')
style.configure("Treeview.Heading", background="lightgreen", foreground="black")

# Treeview scrollbar 
tree_scroll = Scrollbar(cart_frame)
tree_scroll.pack(side=RIGHT, fill=Y)

column_names = ("price", "qty", "total_price", "b_id")
treeview_items = ttk.Treeview(cart_frame, columns=column_names, yscrollcommand=tree_scroll.set)


treeview_items.heading('#0', text="Product Name")
treeview_items.heading('price', text="Price")
treeview_items.heading('qty', text="Qty")
treeview_items.heading('total_price', text="Total Price")
treeview_items.heading('b_id', text="ID")
# align items in a list 
treeview_items.column("#0", anchor=W)
treeview_items.column("price", anchor=CENTER)
treeview_items.column("qty", anchor=CENTER, minwidth=0, width=120)
treeview_items.column("total_price", anchor=CENTER)
treeview_items.column("b_id", anchor=CENTER, minwidth=0, width=120)

# insert items to list 
treeview_items.pack(fill=tk.BOTH, expand=True)

tree_scroll.config(command=treeview_items.yview)
 
# Create treeview items count
count_label = Label(cart_frame, text="Total product: ")
count_label.pack()
count = Entry(cart_frame, width=10)
count.pack()

remove = Button(cart_frame, text="Remove One Selected", command=deleteOne, pady=4, bg="red", fg="white")
remove.pack()

cart_frame.grid(row=3, column=0, padx=5)


# create frame for order details 
order_frame = LabelFrame(root, text="Order Details", padx=5, pady=5)

# create text box labels and input boxes for order details
sub_total = Label(order_frame, text="Sub total")
sub_total.grid(row=0, column=0)
sub_total_amount = Entry(order_frame, width=40)
sub_total_amount.grid(row=0, column=1)

discount = Label(order_frame, text="Discount")
discount.grid(row=1, column=0)
discount_amount = Entry(order_frame, width=40)
discount_amount.grid(row=1, column=1)

payable = Label(order_frame, text="Payable Amount")
payable.grid(row=2, column=0)
payable_amount = Entry(order_frame, width=40)
payable_amount.grid(row=2, column=1)

cash_received = Label(order_frame, text="Cash Received")
cash_received.grid(row=3, column=0)
cash_received_amount = Entry(order_frame, width=40)
cash_received_amount.grid(row=3, column=1)

cash_return = Label(order_frame, text="Cash Return")
cash_return.grid(row=4, column=0)
cash_return_amount = Entry(order_frame, width=40)
cash_return_amount.grid(row=4, column=1)

# gift_calculate = Button(order_frame, command=giftCalculate, text="Calculate Gift", padx=20, bg="green", fg="white")
# gift_calculate.grid(row=5, column=0)

proceed_btn = Button(order_frame, command=proceedOrdering, text="Proceed Order", padx=20, bg="green", fg="white")
proceed_btn.grid(row=5, column=1)

order_frame.grid(row=0, column=1)

# create frame for print button 
print_frame = Frame(root, padx=10, pady=10)

print_btn = Button(print_frame, command=printVoucher, text="Print", padx=20, bg="green", fg="white")
print_btn.grid(row=0, column=0)

reset_btn = Button(print_frame, command=clearForm, text="Reset", padx=20, bg="Red", fg="white")
reset_btn.grid(row=0, column=1)

print_frame.grid(row=1, column=1)

# create frame for report generation
# report_frame = Frame(root, padx=10, pady=10)

# one_day_btn = Button(report_frame, command=todays_sale, text="View Today's Sales", padx=20, bg="Teal", fg="white")
# one_day_btn.grid(row=0, column=0)

# one_month_btn = Button(report_frame, command=one_month_sale, text="View this Month's Sales", padx=20, bg="Teal", fg="white")
# one_month_btn.grid(row=0, column=1)

# report_frame.grid(row=2, column=1)

root.resizable(False,False)
root.mainloop()
