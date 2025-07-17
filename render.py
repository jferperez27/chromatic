import tkinter
import tkinter.font
from tkinter import ttk
from browse import URL
from browse import Text
import browse as b
import re

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
        tokens = b.lex(body)

        self.display_list = Layout(tokens).display_list
        self.tokens = tokens
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
            self.display_list = Layout(self.tokens).display_list
            self.draw()

class Layout:
    def __init__(self, tokens):
        self.display_list = []
        self.line = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 12

        for tok in tokens:
            self.token(tok)
        
        self.flush()

    def token(self, tok):
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)
            #for match in re.finditer(r'\S+|\s+', tok.text.split):
            #    self.word(match.group())
        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4
        elif tok.tag == "br":
            self.flush()
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += VSTEP
    
    def word(self, word):
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)

        if self.cursor_x + w > WIDTH - HSTEP:
            # if out of range
            self.flush()
                
        #self.display_list.append((self.cursor_x, self.cursor_y, word, font))
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent
        iterate = 0
        for (x, word, font) in self.line:
            print(iterate)
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))
            #if iterate == 1:
              #  break
            #iterate += 1
            #break
        
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        self.cursor_x = HSTEP
        self.line = []

def get_font(size, weight, style):
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

if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
