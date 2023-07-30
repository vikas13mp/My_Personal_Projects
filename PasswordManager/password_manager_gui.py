#password manager | GUI |DB

from tkinter import CENTER, Tk,Label, Button, Entry,Frame,END, Toplevel
from tkinter import ttk
from db_operations import DbOperations
import tkinter as tk


class root_window:

    def __init__(self,root,db):
        #db define
        self.db=db  
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("900x550+40+40")

        head_title = Label(self.root, text="Password Manager",width=40,bg="purple",font=("Ariel",20),padx=10,pady=10, justify=CENTER, anchor="center").grid(columnspan=4, padx=140,pady=20)

        self.crud_frame= Frame(self.root, highlightbackground="black",highlightthickness=1,padx=10,pady=30)
        self.crud_frame.grid()
        self.create_entry_labels()
        self.create_entry_boxes()
        self.create_crud_buttons()

        #search button

        self.search_entry = Entry (self.crud_frame,font=("Ariel",12),bg="lightgray")
        self.search_entry.grid(row=self.row_no,column=self.col_no)
        
        self.col_no+=1

        Button(self.crud_frame,text="search",bg='yellow',font=("Ariel",12),width=19).grid(row=self.row_no,column=self.col_no ,padx=5,pady=5)
        
        
        
        self.create_records_tree()

    def create_entry_labels(self):
        self.col_no, self.row_no=0, 0
        labels_info =('Email','Website','Username','Password')
        for label_info in labels_info:
            Label(self.crud_frame,text=label_info ,bg='gray',fg='white',font=('Ariel',12), padx=5, pady=2).grid(row=self.row_no,column=self.col_no, padx=5, pady=2)
            self.col_no+=1

    def create_crud_buttons(self):
        self.row_no+=1
        self.col_no = 0
        buttons_info = (('Save','green',self.save_record),('Update','blue',self.update_record),('Delete','red',self.delete_record),('copy password','violet',self.copy_password),('Show All records','purple',self.show_records))
        for btn_info in buttons_info:
            if btn_info[0]=='Show All records':
                self.row_no+=1
                self.col_no=0
            Button(self.crud_frame,text=btn_info[0] ,bg=btn_info[1],fg='white',font=('Ariel',12), padx=2, pady=1,width=19,command=btn_info[2]).grid(row=self.row_no,column=self.col_no, padx=5, pady=10)
            self.col_no+=1

    def create_entry_boxes(self):
        self.row_no+=1
        self.entry_boxes = []
        self.col_no = 0
        for i in range(4):
            show=""
            if i == 3:
                show = "*"
            entry_box = Entry(self.crud_frame, width=20 ,background="lightgrey", font=("Ariel", 12),show=show)
            entry_box.grid(row=self.row_no,column=self.col_no, padx=5 ,pady=2)
            self.col_no+=1
            self.entry_boxes.append(entry_box)

    #CRUD FUNTIONS

    def save_record(self):
        gmail_id = self.entry_boxes[0].get()
        website = self.entry_boxes[1].get()
        username = self.entry_boxes[2].get()
        password = self.entry_boxes[3].get()
        
        data ={'gmail_id':gmail_id,'website':website,'username':username,'password':password}
        self.db.create_record(data)
        self.show_records()

    def update_record(self):
        gmail_id = self.entry_boxes[1].get()
        website = self.entry_boxes[2].get()
        username = self.entry_boxes[3].get()
        password = self.entry_boxes[4].get()
        
        data ={'gmail_id':gmail_id,'website':website,'username':username,'password':password}
        self.db.update_record(data)
        self.show_records()

    def delete_record(self):
        ID = self.entry_boxes[0].get()
        self.db.delete_record(ID)
        self.show_records()

    ## backend for search 
    def search_record(self):
       return None

    def show_records(self):
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        records_list = self.db.show_records()
        for record in records_list:
            self.records_tree.insert('',END,values=record)

    def create_records_tree(self):
        columns =('ID', 'website','username','password')
        self.records_tree = ttk.Treeview(self.root, columns=columns,show='headings')
        self.records_tree.heading('ID',text="ID")
        self.records_tree.heading('website',text="Website Name")
        self.records_tree.heading('username',text="Username")
        self.records_tree.heading('password',text="Password")
        self.records_tree['displaycolumns'] = ('website','username')

        def item_selected(event):
            for selected_item in self.records_tree.selection():
                item = self.records_tree.item(selected_item)
                record = item['values']
                for entry_box, item in zip(self.entry_boxes, record):
                    entry_box.delete(0, END)
                    entry_box.insert(0, item)

        self.records_tree.bind('<<TreeviewSelect>>',item_selected)

        self.records_tree.grid()

#copy to clickboard like a popup
    def copy_password(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.entry_boxes[3].get())
        message = "Password Copied"
        title = "Copy"
        if self.entry_boxes[3].get()=="":
            message="Box is Empty"
            title="Error"
        self.showmessage(title, message)

    def showmessage(self, title_box:str=None, message:str=None):
        TIME_TO_WAIT = 900 #millisecond 
        root = Toplevel(self.root)
        background ="green"
        if title_box == "Error":
            background="red"
        root.geometry("200x30+600+200")
        root.title(title_box)
        Label(root,text=message, background=background,font=("Ariel",15),fg='white').pack(pady=2)
        try:
            root.after(TIME_TO_WAIT,root.destroy)
        except Exception as e:
            print("Error occured", e)


    

if __name__=="__main__":

#create table if doesn't exist
    db_class=DbOperations()
    db_class.create_table()

    #create tkinter window
    root = Tk()
    root_class =root_window(root,db_class)
    root.mainloop() 