from tkinter import *


def on_button_click(val):
    print(f"Button clicked! {val}")


def main():
    root = Tk()
    root.title("MTG Card Catalog")
    root.geometry("800x600")  # width x height
    my_label = Label(root, text="Welcome to the MTG Card Catalog!")
    my_entry_box = Entry(root)
    my_button = Button(
        root, text="Search", command=lambda: on_button_click(my_entry_box.get())
    )
    my_label.pack()  # Places the label in the window
    my_entry_box.pack()
    my_button.pack()  # Places the button in the window
    root.mainloop()


if __name__ == "__main__":
    main()
