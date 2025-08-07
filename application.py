import sqlite3
from tkinter import *
from enums import Rarity, Color
from database_search import Search_Results

name_to_rarity = {
    "COMMON" :Rarity.COMMON,
    "UNCOMMON":Rarity.UNCOMMON,
    "RARE" :Rarity.RARE,
    "MYTHIC_RARE":Rarity.MYTHIC_RARE,
}

def on_button_click(title, type, subtype, rarity, color, set_shortened):
    print(title,',', type,',',  subtype,',',  rarity,',',  color,',',  set_shortened)
    conn = sqlite3.connect("card_db.db")
    cursor = conn.cursor()
    sr = Search_Results(cursor)
    try:
        tmp_rarity = name_to_rarity[rarity]
    except KeyError:
        tmp_rarity = Rarity.UNKNOWN
    cards = sr.multi_command_building(
        title,
        set_shortened,
        color,
        tmp_rarity,
        type,
        subtype
    )
    print(len(cards))
    for each in cards:
        print(
            f"Set:{each.set:<6}\tR:{each.rarity.name:<12}\tID:{each.id:>6}\t Title: ",
            each.title,
        )
    conn.close()

def main():
    root = Tk()
    root.title("MTG Card Catalog")
    root.geometry("800x600")  # width x height
    my_label = Label(root, text="Welcome to the MTG Card Catalog!")
    my_label.pack()  # Places the label in the window
    Label(root, text = "Title").pack()
    title_entry_box = Entry(root)
    title_entry_box.pack()
    
    Label(root, text = "Type").pack()
    type_entry_box = Entry(root)
    type_entry_box.pack()
    
    Label(root, text = "Subtype").pack()
    subtype_entry_box = Entry(root)
    subtype_entry_box.pack()

    Label(root, text = "Rarity").pack()
    active_var = StringVar(root)
    rarity_drop_box = OptionMenu(root, active_var, Rarity.COMMON.name, Rarity.UNCOMMON.name, Rarity.RARE.name, Rarity.MYTHIC_RARE.name)
    rarity_drop_box.pack()

    Label(root, text = "Color").pack()
    active_var2 = StringVar(root)
    color_drop_box = OptionMenu(root,active_var2, *(Color.keys()))
    color_drop_box.pack()

    Label(root, text = "Set").pack()
    set_entry_box = Entry(root)
    set_entry_box.pack()

    my_button = Button(
        root, text="Search", command=lambda: on_button_click(title_entry_box.get(), type_entry_box.get(), subtype_entry_box.get(), active_var.get(), active_var2.get(), set_entry_box.get())
    )
    my_button.pack()  # Places the button in the window
    root.mainloop()


if __name__ == "__main__":
    main()
