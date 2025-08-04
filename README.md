
# Chromatic Web Browser


Chromatic Browser is a lightweight rendering engine built from scratch in Python to demonstrate the fundamentals of modern browser design. 
It implements a full pipeline from network requests and HTML parsing to CSS styling, layout, and painting using custom-built parsing 
and rendering logic without relying on external browser libraries. This project showcases systems-level design, parsing, and graphics 
rendering skills through a modular and extensible architecture.

**Chromatic is a fully standalone browser built without external frameworks or packages — only Python's standard library.**

Inspired by *Web Browser Engineering* by Pavel Panchekha and Chris Harrelson, 
Chromatic was designed for my own personal curiosity of web 
browsers while studying the Chromium source code.
Chromatic handles industry standards of all browsers in pure Python. It's a minimal, yet functional 
web browser; ideal for educational purposes and low-level systems exploration.
  


## Features
**HTML Parsing and Rendering Pipeline**
- Built a browser pipeline in pure Python. The program is composed of HTTP requests to HTML parsing, layout, and rendering without the use of any external libraries.

**Custom Rendering Engine**
- Developed a window-based rendering system with custom scrolling logic, enabling smooth viewport scrolling without altering canvas coordinates.  

**CSS Parser with Cascade and Specificity**
- Designed a CSS parser enforcing cascade rules, property inheritance, and rule specificity.  
- Supports tag selectors, inline styles, and external stylesheets, merging them into a unified computed style tree.  

**Font Handling**
- Engineered full CSS font support including `font-size`, `font-weight`, and `font-style`.  
- Dynamically converts CSS pixel units into Tkinter font points for consistent, cross-platform text rendering.  

**Color/Background Rendering**
- Applies CSS `color` to text and `background-color` to block elements.  
- Utilizes a layered `display_list` to ensure proper element stacking and maintain visual fidelity.  

**User Agent Stylesheet**
- Bundles a `browser.css` file defining baseline rules (e.g., blue hyperlinks, bold `<b>`, italic `<i>`), ensuring consistent default styles across webpages.

**Error Handling**
- Developed fault-tolerant CSS parsing that skips any malformed declarations 
without interrupting rendering.
  
## Run Locally  
Clone the project  

~~~bash  
  git clone https://link-to-project
~~~

Navigate to project directory  

~~~bash  
  cd chromatic
~~~

Render a webpage

~~~bash  
  python3 main.py https://browser.engineering/examples/xiyouji.html
~~~  
> *Note: URL must include 'HTTPS' or HTTP'*