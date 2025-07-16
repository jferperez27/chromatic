import tkinter
from tkinter import ttk
from browse import URL
import browse as b

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100
MAX_Y = 600


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT,
            scrollregion=(0, 0, WIDTH, HEIGHT)
        )
        self.canvas.pack(fill="both", expand=True)
        self.scroll = 0
        self.window.title("Chromatic")
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mousewheel)
        self.window.bind("<Configure>", self.window_resize)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.window, 
                                  orient="vertical", 
                                  command = self.on_scroll)
        self.scrollbar.place(relx = 1, rely = 0, relheight = 1, anchor = "ne")

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
        Visualizes all characters onto screen.
        """
        max_bottom = HEIGHT

        self.canvas.delete("all")
        for x, y, c in self.display_list:
            max_bottom = max(max_bottom, y)
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c)

        self.max_scroll = max(0, max_bottom - self.canvas.winfo_height())

        ## Update scrollbar y-value logic

        self.canvas.config(scrollregion=(0, 0, WIDTH, self.max_scroll))

        ## Custom scrolling logic

        start_frac = self.scroll / self.max_scroll if self.max_scroll else 0.0
        visible_frac = self.canvas.winfo_height() / self.max_scroll if self.max_scroll else 1.0
        self.scrollbar.set(start_frac, start_frac + visible_frac)


    def scrolldown(self, e):
        """
        Handles down arrow key event.
        """
        pros_scroll = self.scroll + SCROLL_STEP

        if pros_scroll > self.max_scroll:
            self.scroll = self.max_scroll
        else:
            self.scroll += SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        """
        Handles up arrow key event.
        """
        pros_scroll = self.scroll - SCROLL_STEP

        if not pros_scroll < 0:
            self.scroll -= SCROLL_STEP
            self.draw()
        else:
            self.scroll = 0
            self.draw()

    def mousewheel(self, e):
        """
        Handles basic scrolling gesture event.
        """
        print(e.delta)

        # limiter
        if hasattr(self, "scrolling"):
            if self.scrolling == True:
                return

        # OS inertia normalization
        if sys.platform == "darwin":
            delta = e.delta
        else:
            delta = e.delta / 120

        pros_scroll_loc = self.scroll + (-1 * delta * 5)
        
        # DEBUG --
        #print(f"pros {pros_scroll_loc}")
        #print(f"cur {self.scroll}")

        if pros_scroll_loc < 0:
            self.scroll = 0
        elif self.max_scroll > pros_scroll_loc:
            self.scroll = pros_scroll_loc
        else:
            if self.scroll == self.max_scroll:
                return
            else:
                self.scroll = self.max_scroll

        self.scrolling = True
        self.canvas.after(10, self.throttle_draw)

    def throttle_draw(self):
        """
        Calls on draw to update visuals, used by mousewheel() to limit calls
        on draw, decrease overall hardware strain.
        """
        self.draw()
        self.scrolling = False

    def on_scroll(self, *args):
        """
        Handles basic mouse scrolling gesture event.
        """
        if args[0] == "moveto":
            frac = float(args[1])
            self.scroll = frac * self.max_scroll
        elif args[0] == "scroll":
            units = int(args[1])
            self.scroll += units * 40
        self.scroll = max(0, min(self.scroll, self.max_scroll))
        self.draw()

    def window_resize(self, e):
        """
        Handles window resize logic.
        """
        global WIDTH, HEIGHT
        if e.width != WIDTH and e.height != HEIGHT:
            WIDTH = e.width
            HEIGHT = e.height
            self.draw()

def layout(text):
    """
    Formulates list containing all text and x,y coords for each character
    """
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    # for c in text:
    #     display_list.append((cursor_x, cursor_y, c))
    #     cursor_x += HSTEP
    #     if cursor_x >= WIDTH - HSTEP:
    #         cursor_y += VSTEP
    #         cursor_x = HSTEP
    # return display_list

    for line in text.split("\n"):
        for word in line.split():
            width = len(word) * HSTEP
            if cursor_x + width >= WIDTH - HSTEP:
                # if out of range
                cursor_x = HSTEP
                cursor_y += 2 ## Originally: VSTEP
            for char in word:
                display_list.append((cursor_x, cursor_y, char))
                cursor_x += HSTEP
            cursor_x += HSTEP

        cursor_y += VSTEP ## Originally: VSTEP*2
        cursor_x = HSTEP

    return display_list


if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
