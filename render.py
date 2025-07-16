import tkinter
from browse import URL
import browse as b


WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mousewheel)

    def load(self, url):
        """
        Obtains source code, delegates to other methods.
        """
        body = url.request()
        text = b.lex(body)

        self.display_list = layout(text)
        self.draw()

    def draw(self):
        """
        Visualizes all characters onto screen
        """
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def scrolldown(self, e):
        """
        Handles down arrow key event
        """
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        """
        Handles up arrow key event
        """
        pros_scroll = self.scroll - SCROLL_STEP

        if not pros_scroll < 0:
            self.scroll -= SCROLL_STEP
            self.draw()

    def mousewheel(self, e):
        """
        Handles basic scrolling gesture event
        """
        direction = int(e.delta)

        if direction == 1:
            self.scrolldown(e)
        elif direction == -1:
            self.scrollup(e)


def layout(text):
    """
    Formulates list containing all text and x,y coords for each character
    """
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list

if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
