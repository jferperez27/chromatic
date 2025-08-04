import tkinter.font

FONTS = {}

def tree_to_list(tree, list):
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list

class DrawText:
    def __init__(self, x1, y1, text, font, color):
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.color = color
        self.bottom = y1 + font.metrics('linespace')

    def execute(self, scroll, canvas):
        canvas.create_text(
            self.left, self.top - scroll,
            text = self.text,
            font = self.font,
            fill = self.color,
            anchor='nw')

class DrawRect:
    def __init__(self, x1, y1, x2, y2, color):
        self.top = y1
        self.left = x1
        self.bottom = y2
        self.right = x2
        self.color = color

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.left, self.top - scroll,
            self.right, self.bottom - scroll,
            width = 0,
            fill = self.color
        )

def get_font(size, weight, style):
    """
    Stores font if not in cache memory, otherwise stores font for future
    reference. Impactful for Windows and Linux, not so much for MacOS.
    """
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(
            size=size,
            weight=weight,
            slant=style
            )
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]