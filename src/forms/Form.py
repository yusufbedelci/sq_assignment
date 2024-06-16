class BaseForm:
    def __init__(self, root):
        self.root = root

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
