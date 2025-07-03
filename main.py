# main.py

from interface import App
import customtkinter as ctk

def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
