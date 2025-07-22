import tkinter
import tkinter.font
from tkinter import ttk
from browse import URL
from browse import Text
import browse as b
import sys

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100
MAX_Y = 600
FONTS = {}


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
        self.nodes = b.HTMLParser(body).parse()
        b.print_tree(self.nodes)

        self.display_list = Layout(self.nodes).display_list
        self.draw()

    def draw(self):
        """
        Visualizes all characters onto screen.
        """
        max_bottom = HEIGHT

        self.canvas.delete("all")
        for x, y, word, f in self.display_list:
            max_bottom = max(max_bottom, y)
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=word, font=f, anchor='nw')

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
            self.display_list = Layout(self.nodes).display_list
            self.draw()

class Layout:
    def __init__(self, tokens):
        """
        Sorts through all tokens. 
        """
        self.display_list = []
        self.line = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 12

        # for tok in tokens:
        #     self.token(tok)

        self.recuse(tokens)
        
        self.flush()

    def open_tag(self, tag):
        if tag == "i":
            self.style = "italic"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "small":
            self.size -= 2
        elif tag == "big":
            self.size += 4
        elif tag == "br":
            self.flush()

    def close_tag(self, tag):
        if tag == "i":
            self.style = "roman"
        elif tag == "b":
            self.weight = "normal"
        elif tag == "small":
            self.size += 2
        elif tag == "big":
            self.size -= 4
        elif tag == "p":
            self.flush()
            self.cursor_y += VSTEP

    def recuse(self, tree):
        if isinstance(tree, Text):
            for word in tree.text.split():
                self.word(word)
        else:
            self.open_tag(tree.tag)
            for child in tree.children:
                self.recuse(child)
            self.close_tag(tree.tag)

    # def token(self, tok):
    #     """
    #     Checks what type of token a token is, delegates to specific function.
    #     """
    #     if isinstance(tok, Text):
    #         for word in tok.text.split():
    #             self.word(word)
    #     elif tok.tag == "i":
    #         self.style = "italic"
    #     elif tok.tag == "/i":
    #         self.style = "roman"
    #     elif tok.tag == "b":
    #         self.weight = "bold"
    #     elif tok.tag == "/b":
    #         self.weight = "normal"
    #     elif tok.tag == "small":
    #         self.size -= 2
    #     elif tok.tag == "/small":
    #         self.size += 2
    #     elif tok.tag == "big":
    #         self.size += 4
    #     elif tok.tag == "/big":
    #         self.size -= 4
    #     elif tok.tag == "br":
    #         self.flush()
    #     elif tok.tag == "/p":
    #         self.flush()
    #         self.cursor_y += VSTEP
    
    def word(self, word):
        """
        Gets a word, sets font, finds appropriate location for rendering,
        adds to self.line while updating x, y values for future words.
        """
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)

        if self.cursor_x + w > WIDTH - HSTEP:
            # if out of range
            self.flush()
                
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        """
        Gathers font metrics, computes a baseline for all words, computes
        y-pos for all words so they all sit on baseline, adds these values to
        display_list, y-value step down, resets self.line for upcoming lines.
        """
        if not self.line: return
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        for (x, word, font) in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))
        
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        self.cursor_x = HSTEP
        self.line = []

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

# if __name__ == "__main__":
#     import sys
#     Browser().load(URL(sys.argv[1]))
#     tkinter.mainloop()

def start(arg):
    Browser().load(URL(arg))
    tkinter.mainloop()