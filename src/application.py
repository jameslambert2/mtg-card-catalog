"""
application.py

Created By: James Lambert
Updated: 11 Aug 2025

This file when executed creates a GUI with Tkinter that allows a user to 
search through the database using sqlite3 for all available cards and/or sets.

When search results are found, the card image can be pulled by selecting it
and clicking the button labeled "View"
"""

import sqlite3
from tkinter import (
    Toplevel,
    Button,
    Label,
    Tk,
    Scrollbar,
    Entry,
    StringVar,
    OptionMenu,
    RIGHT,
    LEFT,
    BOTH,
    BOTTOM,
    Y,
)
from tkinter import ttk
from urllib.request import urlopen
import io

from PIL import Image, ImageTk

from .update_db.enums import Rarity, Color
from .update_db.card import name_to_rarity
from .database_search import SearchResults, DB_FILE

def on_button_click(args: tuple):
    """
    Button Command to perform the search based on the values in the GUI

    Args:
        args: tuple
            title: str
            type: str
            subtype: str
            rarity: Rarity
            color: str
            set_shortened: str
    """
    title, card_type, subtype, rarity, color, set_shortened = args
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    sr = SearchResults(cursor)
    try:
        tmp_rarity = name_to_rarity[rarity]
    except KeyError:
        tmp_rarity = Rarity.UNKNOWN
    cards = sr.multi_command_building(
        title=title,
        set_shortened=set_shortened,
        color=color,
        rarity=tmp_rarity,
        card_type=card_type,
        subtype=subtype,
    )

    result(cards)
    conn.close()


def grab_image(card_id):
    """
    Grab the individual card image from online

    Args:
        id: int
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    sr = SearchResults(cursor)
    card = sr.get_card_by_id(card_id)
    with urlopen(card.img_url) as u:
        raw_data = u.read()

    image_pil = Image.open(io.BytesIO(raw_data))
    image_tk = ImageTk.PhotoImage(image_pil)
    window = Toplevel()
    window.title("Card Image")
    label = Label(window, image=image_tk)
    label.image = image_tk
    label.pack()
    conn.close()


def result(results):
    """initialization function for Result

    Initialization function for the Result class. It will show the results
    of the search provided before the function call

    Args:
        results: List[DbCard]
    """
    window = Toplevel()
    window.title("Results")

    scrollbar = Scrollbar(window)
    scrollbar.pack(side=RIGHT, fill=Y)
    mylist = ttk.Treeview(window, yscrollcommand=scrollbar.set)
    mylist["columns"] = ("ID", "Set", "Title")

    mylist.heading("ID", text="ID")
    mylist.heading("Set", text="Set")
    mylist.heading("Title", text="Title", anchor="w")
    mylist.column("#0", width=0, anchor="w")
    mylist.column("ID", width=80, anchor="w")
    mylist.column("Set", width=80, anchor="w")
    mylist.column("Title", width=300, anchor="w")
    for each in results:
        mylist.insert(
            "", "end", values=(f"{each.card_id}", f"{each.set}", f"{each.title}")
        )

    mylist.pack(side=LEFT, fill=BOTH)

    button = Button(
        window,
        text="View",
        command=lambda: grab_image(results[int(mylist.focus()[1:], 16) - 1].card_id),
    )
    button.pack(side=BOTTOM, anchor="s")

    scrollbar.config(command=mylist.yview)
    window.bind("<Return>", lambda event=None: button.invoke())


def main():
    """Main application function

    Function to run the original GUI and all of the application 
    revolves around this function call
    
    """
    root = Tk()
    root.title("MTG Card Catalog")
    root.geometry("250x250")  # width x height
    my_label = Label(root, text="Welcome to the MTG Card Catalog!")
    my_label.grid(row=0, column=0, columnspan=3)
    tmp = Label(root, text="Title")
    tmp.grid(row=1, column=0)
    title_entry_box = Entry(root)
    title_entry_box.grid(row=1, column=1)

    tmp = Label(root, text="Type")
    tmp.grid(row=2, column=0)
    type_entry_box = Entry(root)
    type_entry_box.grid(row=2, column=1)

    tmp = Label(root, text="Subtype")
    tmp.grid(row=3, column=0)
    subtype_entry_box = Entry(root)
    subtype_entry_box.grid(row=3, column=1)

    tmp = Label(root, text="Rarity")
    tmp.grid(row=4, column=0)
    active_var = StringVar(root)
    rarity_drop_box = OptionMenu(
        root,
        active_var,
        "",
        Rarity.COMMON.name,
        Rarity.UNCOMMON.name,
        Rarity.RARE.name,
        Rarity.MYTHIC_RARE.name,
    )
    rarity_drop_box.config(width=15)
    rarity_drop_box.grid(row=4, column=1)

    tmp = Label(root, text="Color")
    tmp.grid(row=5, column=0)
    active_var2 = StringVar(root)
    tmp = list(Color.keys())
    tmp.remove("VARIABLE")
    color_drop_box = OptionMenu(root, active_var2, "", *(tmp))
    color_drop_box.config(width=15)
    color_drop_box.grid(row=5, column=1)

    tmp = Label(root, text="Set")
    tmp.grid(row=6, column=0)
    set_entry_box = Entry(root)
    set_entry_box.grid(row=6, column=1)

    my_button = Button(
        root,
        text="Search",
        command=lambda: on_button_click(
            (
                title_entry_box.get(),
                type_entry_box.get(),
                subtype_entry_box.get(),
                active_var.get(),
                active_var2.get(),
                set_entry_box.get(),
            )
        ),
    )
    my_button.grid(row=7, column=1)
    root.bind("<Return>", lambda event=None: my_button.invoke())
    root.mainloop()


if __name__ == "__main__":
    main()
