# Import all the necessary Modules and Library
from tkinter import *
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter import filedialog
import csv
import mysql.connector  
import subprocess 

# Function to connect to the database and show a popup message
def connect_db():
    try:
        global conn
        conn = mysql.connector.connect(
            host='localhost',      
            user='root',                            
            password='root',    # pass word of your root user 
            database='improt_tms' # database name             
        )
        global cur
        cur = conn.cursor()
        conn.commit()
        messagebox.showinfo('Database Connection', 'Successfully connected to the database!')

    except Exception as e:
        messagebox.showerror('Database Error', f'Error connecting to the database: {e}')

# Tables with associated fields
TABLES = ["TaxPayer", "Tax Officer", "Taxes", "Payment", "Tax Assessment", "Tax Audit", "Penalty"]

def open_operation_window(operation):
    # Create a new window for the operation
    window = Toplevel()
    window.title(f"{operation} Operation")

    # Dropdown for selecting the table
    table_var = StringVar(value=TABLES[0])
    table_label = Label(window, text="Select Table:")
    table_label.pack(pady=5)
    table_dropdown = ttk.Combobox(window, textvariable=table_var, values=TABLES)
    table_dropdown.pack(pady=5)

    # Entry fields frame
    global fields_frame
    fields_frame = Frame(window)
    fields_frame.pack(pady=10)

    def generate_fields():
        # Clear previous fields
        for widget in fields_frame.winfo_children():
            widget.destroy()

        selected_table = table_var.get()

        if operation == 'add':
            if selected_table == "TaxPayer":
                create_fields(fields_frame, ["Name", "City", "Email", "PAN", "DOB", "Contact"])
            elif selected_table == "Tax Officer":
                create_fields(fields_frame, ["Name", "Department", "City", "Contact Number"])
            elif selected_table == "Taxes":
                create_fields(fields_frame, ["Tax Name"])
            elif selected_table == "Payment":
                create_fields(fields_frame, ["Taxpayer Id", "Tax Id", "Payment Date", "Amount Paid", "Payment Method"])
            elif selected_table == "Penalty":
                messagebox.showwarning("Operation Not Allowed", "Add operation not allowed on Penalty table")
                return
            elif selected_table == "Tax Assessment":
                create_fields(fields_frame, ["Tax Id", "Taxpayer Id", "Tax Name", "Assessment Date", "Due Date", "Amount"])
            elif selected_table == "Tax Audit":
                create_fields(fields_frame, ["Taxpayer Id", "Tax Id", "Audit Date", "Officer Id"])

        elif operation == 'update':
            if selected_table == "TaxPayer":
                create_fields(fields_frame, ["Taxpayer Id", "Name", "City", "Email", "PAN", "DOB", "Contact"])
            elif selected_table == "Tax Officer":
                create_fields(fields_frame, ["Officer Id", "Name", "Department", "City", "Contact Number"])
            elif selected_table == "Taxes":
                create_fields(fields_frame, ["Tax Id", "Tax Name"])
            elif selected_table == "Payment":
                create_fields(fields_frame, ["Payment Id", "Taxpayer Id", "Tax Id", "Payment Date", "Amount Paid", "Payment Method"])
            elif selected_table == "Tax Assessment":
                create_fields(fields_frame, ["Assessment Id", "Tax Id", "Taxpayer Id", "Tax Name", "Assessment Date", "Due Date", "Amount"])
            elif selected_table == "Tax Audit":
                create_fields(fields_frame, ["Audit Id", "Taxpayer Id", "Tax Id", "Audit Date", "Officer Id"])

        elif operation == 'delete':
            if selected_table == "TaxPayer":
                create_fields(fields_frame, ["Taxpayer Id"])
            elif selected_table == "Tax Officer":
                create_fields(fields_frame, ["Officer Id"])
            elif selected_table == "Taxes":
                create_fields(fields_frame, ["Tax Id"])
            elif selected_table == "Payment":
                create_fields(fields_frame, ["Payment Id"])
            elif selected_table == "Penalty":
                create_fields(fields_frame, ["Penalty Id"])
            elif selected_table == "Tax Assessment":
                create_fields(fields_frame, ["Assessment Id"])
            elif selected_table == "Tax Audit":
                create_fields(fields_frame, ["Audit Id"])





    # Refresh fields when table is changed
    table_dropdown.bind("<<ComboboxSelected>>", lambda event: generate_fields())

    def save_data():
        selected_table = table_var.get()
        if operation == "add":
            add(selected_table)
        elif operation == "update":
            update(selected_table)
        elif operation == "delete":
            delete(selected_table)

        window.destroy()  # Close the operation window after saving

    def confirm():
        confirm = messagebox.askyesno('Confirm', f'Are you sure you want to {operation}?')
        if confirm:
            save_data()
        else:
            messagebox.showinfo("denied", f"{operation} not done.")
            window.destroy()


    buttontext=operation
    save_button = Button(window, text=buttontext, command=confirm)
    save_button.pack(pady=10)

        

    generate_fields()

def create_fields(parent, fields):
    for field in fields:
        label = Label(parent, text=f"{field}:")
        label.pack(anchor="w")
        entry = Entry(parent, name=field.lower().replace(" ", "_"))
        entry.pack(fill="x", padx=10, pady=5)


def get_field_values():
    # Fetch the values from all the entry fields
    fields = {}
    for widget in fields_frame.winfo_children():
        if isinstance(widget, Entry):
            fields[widget.winfo_name()] = widget.get()
    return list(fields.values())

def add(table):
    field_values = get_field_values()
    if table == "TaxPayer":
        query = "INSERT INTO taxpayer (Name, City, Email, PAN, DOB, contact) VALUES (%s, %s, %s, %s, %s, %s)"
    elif table == "Tax Officer":
        query = "INSERT INTO tax_officer (Name, Department, City, Contact_Number) VALUES (%s, %s, %s, %s)"
    elif table == "Taxes":
        query = "INSERT INTO taxes(Tax_Name) VALUES (%s)"
    elif table == "Payment":
        query = "INSERT INTO payment (Taxpayer_Id, Tax_Id, Payment_Date, Amount_Paid, Payment_Method) VALUES (%s, %s, %s, %s, %s)"
    elif table == "Tax Assessment":
        query = "INSERT INTO tax_assessment (Tax_Id, Taxpayer_Id, Tax_Name, Assessment_Date, Due_Date, Amount) VALUES (%s, %s, %s, %s, %s, %s)"
    elif table == "Tax Audit":
        query = "INSERT INTO tax_audit (Taxpayer_Id, Tax_Id, Audit_Date, Officer_Id) VALUES (%s, %s, %s, %s)"

    cur.execute(query, field_values)
    conn.commit()

    messagebox.showinfo("Success", f"Record added to {table} table.")


def update(table):
    field_values = get_field_values()

    # Determine the ID field and value
    id_field = None
    if table == "TaxPayer":
        query = "UPDATE taxpayer SET Name = %s, City = %s, Email = %s, PAN = %s, DOB = %s, contact = %s WHERE taxpayer_id = %s"
        id_field = "taxpayer_id"
    elif table == "Tax Officer":
        query = "UPDATE tax_officer SET Name = %s, Department = %s, City = %s, Contact_Number = %s WHERE officer_id = %s"
        id_field = "officer_id"
    elif table == "Taxes":
        query = "UPDATE taxes SET Tax_Name = %s WHERE tax_id = %s"
        id_field = "tax_id"
    elif table == "Payment":
        query = "UPDATE payment SET Taxpayer_Id = %s, Tax_Id = %s, Payment_Date = %s, Amount_Paid = %s, Payment_Method = %s WHERE payment_id = %s"
        id_field = "payment_id"
    elif table == "Tax Assessment":
        query = "UPDATE tax_assessment SET Tax_Id = %s, Taxpayer_Id = %s, Tax_Name = %s, Assessment_Date = %s, Due_Date = %s, Amount = %s WHERE assessment_id = %s"
        id_field = "assessment_id"
    elif table == "Tax Audit":
        query = "UPDATE tax_audit SET Taxpayer_Id = %s, Tax_Id = %s, Audit_Date = %s, Officer_Id = %s WHERE audit_id = %s"
        id_field = "audit_id"

    # Check if the record exists
    try:
        id_value = field_values[0]  # first field is the ID
        check_query = f"SELECT COUNT(*) FROM {table.lower().replace(' ', '_')} WHERE {id_field} = %s"
        cur.execute(check_query, (id_value,))
        exists = cur.fetchone()[0] > 0

        if not exists:
            messagebox.showwarning("Update Failed", f"No record found with {id_field} = {id_value}.")
            return

        cur.execute(query, (*field_values[1:], field_values[0]))
        conn.commit()
        messagebox.showinfo("Success", f"Record updated in {table} table.")
    except:
        messagebox.showerror("Error", "oops! Something went wrong.")


def delete(table):
    field_values = get_field_values()

    # Determine the ID field
    id_field = None
    if table == "TaxPayer":
        query = "DELETE FROM taxpayer WHERE taxpayer_id = %s"
        id_field = "taxpayer_id"
    elif table == "Tax Officer":
        query = "DELETE FROM tax_officer WHERE officer_id = %s"
        id_field = "officer_id"
    elif table == "Taxes":
        query = "DELETE FROM taxes WHERE tax_id = %s"
        id_field = "tax_id"
    elif table == "Payment":
        query = "DELETE FROM payment WHERE payment_id = %s"
        id_field = "payment_id"
    elif table == "Tax Assessment":
        query = "DELETE FROM tax_assessment WHERE assessment_id = %s"
        id_field = "assessment_id"
    elif table == "Tax Audit":
        query = "DELETE FROM tax_audit WHERE audit_id = %s"
        id_field = "audit_id"

    # Check if the record exists
    try:
        id_value = field_values[0]  # Assuming the first field is the ID
        check_query = f"SELECT COUNT(*) FROM {table.lower().replace(' ', '_')} WHERE {id_field} = %s"
        cur.execute(check_query, (id_value,))
        exists = cur.fetchone()[0] > 0

        if not exists:
            messagebox.showwarning("Delete Failed", f"No record found with {id_field} = {id_value}.")
            return

        cur.execute(query, field_values)
        conn.commit()
        messagebox.showinfo("Success", f"Record deleted from {table} table.")
    except:
        messagebox.showerror("Error", " You are not permitted to delete this data.")



  







def showtaxpaid():
    values=[]
    window = Toplevel()
    label1=Label(window, text='Tax Payer Id')
    label1.pack(anchor='w')
    entry1 = Entry(window)
    entry1.pack(fill="x", padx=10, pady=5)
    label2=Label(window, text='Tax Id')
    label2.pack(anchor="w")
    entry2 = Entry(window)
    entry2.pack(fill="x", padx=10, pady=5)
    values.append(entry1.get())
    values.append(entry2.get())


    columns = ('Payment ID', 'Tax Payer Name', 'Tax Name', 'Payment Date', 'Amount Paid')
    tree1 = ttk.Treeview(window, columns=columns, show='headings')
    for col in columns:
        tree1.heading(col, text=col)
        tree1.column(col, width=100, anchor='center')  # Adjust column width and alignment
        tree1.pack(fill='both', padx=10, pady=5)

    def enter():
        taxpayer_id = entry1.get()
        tax_id = entry2.get()

        # Clear previous entries in the Treeview
        for row in tree1.get_children():
            tree1.delete(row)

        try:
            # Execute the query
            cur.execute('''SELECT p.payment_id, t.name, x.tax_name, p.payment_date, p.amount_paid 
                           FROM payment p 
                           INNER JOIN taxpayer t USING(taxpayer_id) 
                           INNER JOIN taxes x USING(tax_id) 
                           WHERE p.taxpayer_id=%s AND p.tax_id=%s''', (taxpayer_id, tax_id))
            results = cur.fetchall()

            # Insert results into Treeview
            for row in results:
                tree1.insert('', 'end', values=row)

            if not results:
                messagebox.showinfo("No Records", "No payment records found for the given IDs.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            conn.rollback()


      
    # Create a frame for the buttons
    button_frame = Frame(window)
    button_frame.pack(pady=10)

    # Enter button
    enter_button = Button(button_frame, text='Enter', command=enter)
    enter_button.pack(side=LEFT, padx=20)

    # Done button
    done_button = Button(button_frame, text='Done', command=window.destroy)
    done_button.pack(side=LEFT, padx=20)
    
    


def showpenalty():
    window = Toplevel()
    window.title("Penalty Details")

    # Labels and Entry fields for taxpayer_id, tax_id, and penalty_date
    label1 = Label(window, text='Tax Payer Id')
    label1.pack(anchor='w')
    entry1 = Entry(window)
    entry1.pack(fill="x", padx=10, pady=5)

    label2 = Label(window, text='Tax Id')
    label2.pack(anchor="w")
    entry2 = Entry(window)
    entry2.pack(fill="x", padx=10, pady=5)

    label3 = Label(window, text='Penalty Date (YYYY-MM-DD)')
    label3.pack(anchor="w")
    entry3 = Entry(window)
    entry3.pack(fill="x", padx=10, pady=5)

    # Create Treeview for displaying results
    columns = ('Penalty ID', 'Taxpayer ID', 'Tax ID', 'Penalty Amount', 'Penalty Date')
    tree2 = ttk.Treeview(window, columns=columns, show='headings')

    # Define the column headers
    for col in columns:
        tree2.heading(col, text=col)
        tree2.column(col, width=100, anchor='center')  # Adjust column width and alignment

    tree2.pack(fill="x", padx=10, pady=5)

    def enter():
        taxpayer_id = entry1.get()
        tax_id = entry2.get()
        penalty_date = entry3.get()

        # Clear previous entries in the Treeview
        for row in tree2.get_children():
            tree2.delete(row)

        # Build query dynamically based on provided input
        if not taxpayer_id and not tax_id and not penalty_date:
            query = "SELECT * FROM penalty"
            values = []
        else:
            query = "SELECT * FROM penalty WHERE"
            conditions = []
            values = []

            if taxpayer_id:
                conditions.append(" taxpayer_id = %s")
                values.append(taxpayer_id)
            if tax_id:
                conditions.append(" tax_id = %s")
                values.append(tax_id)
            if penalty_date:
                conditions.append(" penalty_date = %s")
                values.append(penalty_date)

            query += " AND".join(conditions)  # Use AND to combine conditions

        try:
            # Execute the query with provided values
            cur.execute(query, values)
            results = cur.fetchall()

            # Insert results into Treeview
            for row in results:
                tree2.insert('', 'end', values=row)

            if not results and (taxpayer_id or tax_id or penalty_date):
                messagebox.showinfo("No Records", "No penalty records found for the given parameters.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            conn.rollback()

    # Create a frame for the buttons
    button_frame = Frame(window)
    button_frame.pack(pady=10)

    # Enter button
    enter_button = Button(button_frame, text='Enter', command=enter)
    enter_button.pack(side=LEFT, padx=20)

    # Done button
    done_button = Button(button_frame, text='Done', command=window.destroy)
    done_button.pack(side=LEFT, padx=20)



def taxpayerinfo():
    window = Toplevel()
    window.title("Taxpayer Information")

    # Labels and Entry fields for taxpayer_id and name
    label1 = Label(window, text='TaxPayer Id')
    label1.pack(anchor='w')
    entry1 = Entry(window)
    entry1.pack(fill="x", padx=10, pady=5)

    label2 = Label(window, text='TaxPayer Name')
    label2.pack(anchor="w")
    entry2 = Entry(window)
    entry2.pack(fill="x", padx=10, pady=5)

    # Create Treeview for displaying results
    columns = ('Taxpayer ID', 'Name', 'City', 'Email', 'PAN', 'DOB', 'Contact', 'Payment ID', 'Tax ID', 'Payment Date', 'Amount Paid', 'Penalty ID', 'Penalty Amount', 'Penalty Date')
    tree3 = ttk.Treeview(window, columns=columns, show='headings')

    # Define the column headers
    for col in columns:
        tree3.heading(col, text=col)
        tree3.column(col, width=100, anchor='center')  # Adjust column width and alignment

    tree3.pack(fill="x", padx=10, pady=5)

    def enter():
        taxpayer_id = entry1.get()
        name = entry2.get()

        # Clear previous entries in the Treeview
        for row in tree3.get_children():
            tree3.delete(row)

        # Build query dynamically based on provided input
        query = "SELECT * FROM taxpayer LEFT JOIN payment USING(taxpayer_id) LEFT JOIN penalty USING(taxpayer_id) WHERE"
        conditions = []
        values = []

        if taxpayer_id:
            conditions.append(" taxpayer.taxpayer_id = %s")
            values.append(taxpayer_id)
        if name:
            conditions.append(" taxpayer.name = %s")
            values.append(name)

        if not conditions:
            messagebox.showwarning("No Input", "Please provide either Taxpayer ID or Name.")
            return

        # Combine conditions into query string
        query += " OR".join(conditions)

        try:
            # Execute the query with provided values
            cur.execute(query, values)
            results = cur.fetchall()

            # Insert results into Treeview
            for row in results:
                tree3.insert('', 'end', values=row)

            if not results:
                messagebox.showinfo("No Records", "No records found for the given parameters.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            conn.rollback()

    # Create a frame for the buttons
    button_frame = Frame(window)
    button_frame.pack(pady=10)

    # Enter button
    enter_button = Button(button_frame, text='Enter', command=enter)
    enter_button.pack(side=LEFT, padx=20)

    # Done button
    done_button = Button(button_frame, text='Done', command=window.destroy)
    done_button.pack(side=LEFT, padx=20)




def taxofficerinfo():
    window = Toplevel()
    window.title("Tax Officer Information")

    # Labels and Entry fields for officer_id and name
    label1 = Label(window, text='Officer Id')
    label1.pack(anchor='w')
    entry1 = Entry(window)
    entry1.pack(fill="x", padx=10, pady=5)

    label2 = Label(window, text='Officer Name')
    label2.pack(anchor="w")
    entry2 = Entry(window)
    entry2.pack(fill="x", padx=10, pady=5)

    # Create Treeview for displaying results
    columns = ('Officer ID', 'Name', 'Department', 'City', 'Contact Number', 'Audit ID', 'Taxpayer ID', 'Tax ID', 'Audit Date')
    tree4 = ttk.Treeview(window, columns=columns, show='headings')

    # Define the column headers
    for col in columns:
        tree4.heading(col, text=col)
        tree4.column(col, width=100, anchor='center')  # Adjust column width and alignment

    tree4.pack(fill="x", padx=10, pady=5)

    def enter():
        officer_id = entry1.get()
        name = entry2.get()

        # Clear previous entries in the Treeview
        for row in tree4.get_children():
            tree4.delete(row)

        # Build query dynamically based on provided input
        query = "SELECT * FROM tax_officer o LEFT JOIN tax_audit a ON o.officer_id = a.officer_id WHERE"
        conditions = []
        values = []

        if officer_id:
            conditions.append(" o.officer_id = %s")
            values.append(officer_id)
        if name:
            conditions.append(" o.name = %s")
            values.append(name)

        if not conditions:
            messagebox.showwarning("No Input", "Please provide either Officer ID or Name.")
            return

        # Combine conditions into query string
        query += " OR".join(conditions)

        try:
            # Execute the query with provided values
            cur.execute(query, values)
            results = cur.fetchall()

            # Insert results into Treeview
            for row in results:
                tree4.insert('', 'end', values=row)

            if not results:
                messagebox.showinfo("No Records", "No records found for the given parameters.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            conn.rollback()

    # Create a frame for the buttons
    button_frame = Frame(window)
    button_frame.pack(pady=10)

    # Enter button
    enter_button = Button(button_frame, text='Enter', command=enter)
    enter_button.pack(side=LEFT, padx=20)

    # Done button
    done_button = Button(button_frame, text='Done', command=window.destroy)
    done_button.pack(side=LEFT, padx=20)

def paymentlog():
    # Create a new window for the payment log
    window = Toplevel()
    window.title("Payment Log")

    # Treeview for displaying payment records
    columns = ('Payment ID', 'Taxpayer ID', 'Tax ID', 'Payment Date', 'Amount Paid', 'Payment Method')
    tree5 = ttk.Treeview(window, columns=columns, show="headings")

    # Configure Treeview columns
    for col in columns:
        tree5.heading(col, text=col)
        tree5.column(col, width=100, anchor="center")

    # Add vertical scrollbar to Treeview
    scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree5.yview)
    tree5.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    tree5.pack(fill="both", expand=True)

    # Query to fetch payment records
    query = "SELECT * FROM payment"
    
    try:
        # Execute the query
        cur.execute(query)
        rows = cur.fetchall()

        # Insert data into Treeview
        for row in rows:
            tree5.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("Error", str(e))

    # Done button to close the window
    done_button = Button(window, text="Done", command=window.destroy)
    done_button.pack(pady=10)

    



def auditlog():
    # Create a new window for the audit log
    window = Toplevel()
    window.title("Audit Log")

    # Treeview for displaying audit records
    columns = ('Audit ID', 'Taxpayer ID', 'Tax ID', 'Audit Date', 'Officer ID')
    tree6 = ttk.Treeview(window, columns=columns, show="headings")

    # Configure Treeview columns
    for col in columns:
        tree6.heading(col, text=col)
        tree6.column(col, width=100, anchor="center")

    # Add vertical scrollbar to Treeview
    scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree6.yview)
    tree6.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    tree6.pack(fill="both", expand=True)

    # Query to fetch audit records
    query = "SELECT * FROM tax_audit"
    
    try:
        # Execute the query
        cur.execute(query)
        rows = cur.fetchall()

        # Insert data into Treeview
        for row in rows:
            tree6.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("Error", str(e))

    # Done button to close the window
    done_button = Button(window, text="Done", command=window.destroy)
    done_button.pack(pady=10)

    window.mainloop()  # Start the window's event loop

def assesslog():
    # Create a new window for the assessment log
    window = Toplevel()
    window.title("Assessment Log")

    # Treeview for displaying assessment records
    columns = ('Assessment ID', 'Tax ID', 'Taxpayer ID', 'Tax Name', 'Assessment Date', 'Due Date', 'Amount')
    tree7 = ttk.Treeview(window, columns=columns, show="headings")

    # Configure Treeview columns
    for col in columns:
        tree7.heading(col, text=col)
        tree7.column(col, width=100, anchor="center")

    # Add vertical scrollbar to Treeview
    scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree7.yview)
    tree7.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    tree7.pack(fill="both", expand=True)

    # Query to fetch assessment records
    query = "SELECT * FROM tax_assessment"
    
    try:
        # Execute the query
        cur.execute(query)
        rows = cur.fetchall()

        # Insert data into Treeview
        for row in rows:
            tree7.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("Error", str(e))

    # Done button to close the window
    done_button = Button(window, text="Done", command=window.destroy)
    done_button.pack(pady=10)

    

last_query = ""
def show_table_contents(query):
   
    # Clear the treeview
    for i in tree8.get_children():
        tree8.delete(i)

    # Execute the query and insert data into the treeview
    cur.execute(query)
    
    rows = cur.fetchall()
    
    # Define columns for the treeview based on the query result
    columns = [desc[0] for desc in cur.description]
    tree8["columns"] = columns
    
    # Configure columns in the treeview
    for col in columns:
        tree8.heading(col, text=col)
        tree8.column(col, width=100, anchor='center')

    # Insert rows into the treeview
    for row in rows:
        tree8.insert("", END, values=row)

    

def show_taxpayer_table():
    global last_query
    query = "SELECT * FROM taxpayer"
    last_query=query
    show_table_contents(query)

def show_taxofficer_table():
    global last_query
    query = "SELECT * FROM tax_officer"
    last_query=query
    show_table_contents(query)

def show_taxes_table():
    global last_query
    query = "SELECT * FROM taxes"
    last_query=query
    show_table_contents(query)











    

# Function to handle logout
def logout():
    yn=messagebox.askyesno("Logout", "Are you sure you want log out?")
    if not yn:
        return
    else:
        Root.destroy()
        subprocess.Popen(['python', 'Home.py'])  # Restart Home.py

# Initialize the main window
Root = Tk()
Root.geometry('1280x720+0+0')
Root.title("Tax Management System")
Root.resizable(False, False)
bgframe = Frame(Root, bg='#123F5C')
bgframe.place(relx=0.5, rely=0.5, anchor='center', width=1280, height=720)



# Set the title bar of the application
title = Label(Root, text='Tax Management System', font=('Cambria', '40', 'bold'), fg='white', bg='#123F5C')

title.place(relx=0.5, y=40, anchor=CENTER)


# Define a left frame to contain the action buttons
lframe = Frame(Root, width=200, height=1000, bg='#123F5C')
lframe.place(x=30, y=120)

# Define a right frame to contain the action result
rframe = Frame(Root, width=900, height=50, bg='#123F5C',borderwidth=2)
rframe.place(x=300, y=125)


# Treeview frame on the right (positioned absolutely)
tree_frame = Frame(Root)
tree_frame.place(x=305, y=177, width=925, height=480)



# Scrollbars for the Treeview
tree_scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
tree_scroll_y.pack(side=RIGHT, fill=Y)

tree_scroll_x = Scrollbar(tree_frame, orient=HORIZONTAL)
tree_scroll_x.pack(side=BOTTOM, fill=X)

# Create the Treeview widget
tree8 = ttk.Treeview(tree_frame, show="headings")
tree8.pack(fill=BOTH, expand=True)

tree_scroll_y.config(command=tree8.yview)
tree_scroll_x.config(command=tree8.xview)









# Add Buttons in the left frame
butfont=('Georgia',12,'bold')
btn1 = Button(lframe, width=20, height=1, text='Add >',font=butfont, bg='#F59C12', fg='white',relief="raised", borderwidth=3, command=lambda:open_operation_window("add"))
btn1.grid(row=1, column=0, padx=10, pady=7)

btn2 = Button(lframe, width=20, height=1, text='Update >',font=butfont, bg='#F59C12', fg='white',relief="raised", borderwidth=3, command=lambda:open_operation_window("update"))
btn2.grid(row=2, column=0, padx=10, pady=7)

btn3 = Button(lframe, width=20, height=1, text='Delete >',font=butfont, bg='#F59C12', fg='white',relief="raised", borderwidth=3, command=lambda:open_operation_window("delete"))
btn3.grid(row=3, column=0, padx=10, pady=7)



btn5 = Button(lframe, width=20, height=1, text='Show Tax paid',font=butfont, bg='#F59C12', fg='white',relief="raised", borderwidth=3, command=showtaxpaid)
btn5.grid(row=5, column=0, padx=10, pady=7)

btn6 = Button(lframe, width=20, height=1, text='Show penalties',font=butfont, bg='#F59C12', fg='white',relief="raised", borderwidth=3, command=showpenalty)
btn6.grid(row=6, column=0, padx=10, pady=7)

btn7 = Button(lframe, width=20, height=1, text='Show Tax Payer info',font=butfont, bg='#F59C12', fg='white',relief="raised", borderwidth=3, command=taxpayerinfo)
btn7.grid(row=7, column=0, padx=10, pady=7)

btn8 = Button(lframe, width=20, height=1, text='Show Tax Officer info',font=butfont, bg='#F59C12', fg='white',relief="raised", borderwidth=3, command=taxofficerinfo)
btn8.grid(row=8, column=0, padx=10, pady=7)

btn9 = Button(lframe, width=20, height=1, text='Payment log',font=butfont, bg='#F59C12', fg='white',relief="raised", borderwidth=3, command=paymentlog)
btn9.grid(row=9, column=0, padx=10, pady=7)

btn10 = Button(lframe, width=20, height=1, text='Tax audit log',font=butfont, bg='#F59C12', fg='white', command=auditlog)
btn10.grid(row=10, column=0, padx=10, pady=7)

btn11 = Button(lframe, width=20, height=1, text='Tax assessment log',font=butfont, bg='#F59C12', fg='white',relief="raised", borderwidth=3, command=assesslog)
btn11.grid(row=11, column=0, padx=10, pady=7)

btn12 = Button(lframe, width=20, height=1, text='Log Out',font=butfont, bg='#940306', fg='white',relief="raised", borderwidth=3, command=logout)
btn12.grid(row=12, column=0, padx=10, pady=30)




# Configure the buttons to touch each other and fill the frame horizontally
taxpayer_button = Button(rframe, text="Tax Payer", font=butfont, bg='#F59C12', fg='white',relief="raised", borderwidth=3, width=25, height=1, command=show_taxpayer_table)
taxpayer_button.pack(side=LEFT, expand=True, padx=5)

taxofficer_button = Button(rframe, text="Tax Officer", font=butfont, bg='#F59C12', fg='white',relief="raised", borderwidth=3, width=25, height=1, command=show_taxofficer_table)
taxofficer_button.pack(side=LEFT, expand=True, padx=5)

taxes_button = Button(rframe, text="Taxes", font=butfont, bg='#F59C12', fg='white',relief="raised", borderwidth=3, width=25, height=1, command=show_taxes_table)
taxes_button.pack(side=LEFT, expand=True, padx=5)

ref=Image.open('ref2.png').resize((25,25))
refimg=ImageTk.PhotoImage(ref)
refresh_button = Button(rframe,image=refimg, font=butfont, bg='#F59C12', fg='white',relief="raised", borderwidth=3,  command=lambda:show_table_contents(last_query))
refresh_button.pack(side=LEFT, expand=True, padx=5)







# Connect to the database and show the initial message
connect_db()
show_taxpayer_table()
Root.mainloop()



#close the connection when the application exits
if conn.is_connected():
    conn.close()

