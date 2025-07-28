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
BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]


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
        #b.print_tree(self.nodes) TO PRINT TREE IN TERMINAL

        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)

        self.draw()

    def draw(self):
        """
        Visualizes all characters onto screen.
        """
        #max_bottom = HEIGHT
        max_bottom = self.document.height + 2*VSTEP

        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + HEIGHT: continue
            if cmd.bottom < self.scroll: continue
            cmd.execute(self.scroll, self.canvas)

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
        max_y = max(self.document.height + 2*VSTEP - HEIGHT, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)
        self.draw()

    def scrollup(self, e):
        """
        Handles up arrow key event.
        """
        self.scroll = max(self.scroll - SCROLL_STEP, 0)
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
            #paint_tree(self.document, self.display_list)
            self.draw()

class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []

        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        
    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)

        self.width = WIDTH - 2*HSTEP
        self.x = HSTEP
        self.y = VSTEP
        child.layout()
        #self.display_list = child.display_list
        self.height = child.height


    def paint(self):
        return []


class BlockLayout:
    def __init__(self, node, parent, previous):
        """
        Sorts through all tokens. 
        """
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.display_list = []

        ## Default values instead of 'None' to suppress warnings.
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0 


    def layout_mode(self):
        """
        Determines whether an element should be laid out via the recurse,
        flush, or layout_intermediate function.
        """
        if isinstance(self.node, Text):
            return "inline"
        elif any([isinstance(child, b.Element) and \
                  child.tag in BLOCK_ELEMENTS for child in self.node.children]):
            return "block"
        elif self.node.children:
            return "inline"
        else:
            return "block"


    def layout(self):        
        self.x = self.parent.x
        self.width = self.parent.width

        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for child in self.node.children:
                next = BlockLayout(child, self, previous)
                self.children.append(next)
                next.layout()
                previous = next
            self.height = sum([child.height for child in self.children])
        else:
            self.cursor_x = 0
            self.cursor_y = 0
            self.weight = "normal"
            self.style = "roman"
            self.size = 12
            self.line = []
            self.recuse(self.node)
            self.flush()
            self.height = self.cursor_y
    
    def layout_intermediate(self):
        previous = None
        for child in self.node.children:
            next = BlockLayout(child, self, previous)
            self.children.append(next)
            previous = next

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
    
    def word(self, word):
        """
        Gets a word, sets font, finds appropriate location for rendering,
        adds to self.line while updating x, y values for future words.
        """
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)

        if self.cursor_x + w > self.width:
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

        for rel_x, word, font in self.line:
            x = self.x + rel_x
            y = self.y + baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))
        
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        self.cursor_x = 0
        self.line = []

    def paint(self):
        cmds = []
        if isinstance(self.node, b.Element) and self.node.tag == "pre":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(self.x, self.y, x2, y2, "gray")
            cmds.append(rect)
        if self.layout_mode() == "inline":
            for x, y, word, font in self.display_list:
                cmds.append(DrawText(x, y, word, font))
        return cmds

    
class DrawText:
    def __init__(self, x1, y1, text, font):
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = y1 + font.metrics('linespace')

    def execute(self, scroll, canvas):
        canvas.create_text(
            self.left, self.top - scroll,
            text = self.text,
            font = self.font,
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

def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)


def start(arg):
    Browser().load(URL(arg))
    tkinter.mainloop()