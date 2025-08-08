import sqlite3
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from update_db.enums import Rarity, Color
from urllib.request import urlopen
from database_search import Search_Results
import io

name_to_rarity = {
    "COMMON": Rarity.COMMON,
    "UNCOMMON": Rarity.UNCOMMON,
    "RARE": Rarity.RARE,
    "MYTHIC_RARE": Rarity.MYTHIC_RARE,
}


def on_button_click(title, type, subtype, rarity, color, set_shortened):
    conn = sqlite3.connect("card_db.db")
    cursor = conn.cursor()
    sr = Search_Results(cursor)
    try:
        tmp_rarity = name_to_rarity[rarity]
    except KeyError:
        tmp_rarity = Rarity.UNKNOWN
    cards = sr.multi_command_building(
        title, set_shortened, color, tmp_rarity, type, subtype
    )
    Result(cards)
    conn.close()


def grab_image(id):
    conn = sqlite3.connect("card_db.db")
    cursor = conn.cursor()
    sr = Search_Results(cursor)
    card = sr.get_card_by_id(id)
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


class Result:
    def __init__(self, results):
        self.results = results
        self.window = Toplevel()
        self.window.title("Results")

        scrollbar = Scrollbar(self.window)
        scrollbar.pack(side=RIGHT, fill=Y)
        mylist = ttk.Treeview(self.window, yscrollcommand=scrollbar.set)
        mylist["columns"] = ("ID", "Set", "Title")

        mylist.heading("ID", text="ID")
        mylist.heading("Set", text="Set")
        mylist.heading("Title", text="Title", anchor="w")
        mylist.column("#0", width=0, anchor="w")
        mylist.column("ID", width=80, anchor="w")
        mylist.column("Set", width=80, anchor="w")
        mylist.column("Title", width=300, anchor="w")
        for each in self.results:
            mylist.insert(
                "", "end", values=(f"{each.id}", f"{each.set}", f"{each.title}")
            )

        mylist.pack(side=LEFT, fill=BOTH)

        button = Button(
            self.window,
            text="View",
            command=lambda: grab_image(self.results[int(mylist.focus()[1:], 16) - 1].id),
        )
        button.pack(side=BOTTOM, anchor="s")

        scrollbar.config(command=mylist.yview)
        self.window.bind("<Return>", lambda event=None: button.invoke())


def main():
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
            title_entry_box.get(),
            type_entry_box.get(),
            subtype_entry_box.get(),
            active_var.get(),
            active_var2.get(),
            set_entry_box.get(),
        ),
    )
    my_button.grid(row=7, column=1)
    root.bind("<Return>", lambda event=None: my_button.invoke())
    root.mainloop()


if __name__ == "__main__":
    main()
