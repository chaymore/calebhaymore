"""Caleb's own books. Each entry: thickness and height in metres, depth, and a spine design (see art.spine).

The designs are original typographic spines that suggest each edition. They do not copy cover art or publisher marks.
"""
GOLD = "#c9a45a"
CREAM = "#f1ede2"


def _lewis(title, colour):
    return dict(w=0.022, h=0.2, d=0.13, title=title, author="C·S· LEWIS", bg="#f3f0e6", bands=[(0, 0.21, colour), (0.92, 1, colour)],
                author_first=True, author_span=(0.02, 0.19), author_fg="#ffffff", author_font="cinzel", author_align="l", author_scale=0.36,
                title_span=(0.26, 0.88), title_fg=colour, title_font="cinzel", title_scale=0.4, title_spacing=0.05)


def _tolkien(title, colour):
    return dict(w=0.033, h=0.185, d=0.125, title=title, bg=colour, title_fg=GOLD, title_font="cinzel-b", title_span=(0.1, 0.92), title_scale=0.42)


# The shelf in the photo, left to right.
PHOTO_SHELF = [
    dict(case="tolkien", colour="#2a1a15", label="J·R·R· TOLKIEN", books=[
        _tolkien("The HOBBIT", "#4a2a33"), _tolkien("The FELLOWSHIP of the RING", "#a2672b"),
        _tolkien("The TWO TOWERS", "#6b4326"), _tolkien("The RETURN of the KING", "#4f4a2c")]),
    dict(w=0.036, h=0.235, d=0.16, title="MEN ARE FROM MARS, Women Are from Venus", author="JOHN GRAY, Ph.D.", bg="#f1efe8", fg="#1c1c1c",
         title_font="playfair", author_font="oswald", title_scale=0.42, author_scale=0.3, title_span=(0.05, 0.7), author_span=(0.74, 0.9)),
    dict(w=0.03, h=0.245, d=0.16, title="The Very Best of The Federalist Papers", author="Hamilton, Madison, and Jay", bg="#77777a", fg="#ecebe6",
         title_font="garamond-i", author_font="garamond-i", title_scale=0.46, author_scale=0.36, title_span=(0.2, 0.62), author_span=(0.66, 0.95)),
    dict(w=0.055, h=0.2, d=0.13, title="The Count of Monte Cristo", author="DUMAS", bg="#111111", bands=[(0.8, 0.86, "#efece2")],
         author_first=True, author_span=(0.07, 0.2), author_fg="#e2622a", author_font="oswald", author_align="l", author_scale=0.16,
         title_span=(0.24, 0.76), title_font="playfair-i", title_scale=0.24),
    dict(w=0.026, h=0.175, d=0.11, title="THE CHOSEN", author="POTOK", bg="#8d8d8b", fg="#111111", title_font="gothic", author_font="gothic",
         title_scale=0.6, author_scale=0.6, title_span=(0.3, 0.62), author_span=(0.68, 0.9)),
    dict(w=0.03, h=0.235, d=0.16, title="DEEP WORK", author="CAL NEWPORT", bg="#f2c81e", fg="#111111", title_font="gothic", author_font="gothic",
         title_scale=0.86, author_scale=0.7, title_span=(0.04, 0.5), author_span=(0.52, 0.88)),
    dict(w=0.048, h=0.24, d=0.165, title="MOBY DICK", author="HERMAN|MELVILLE", upright=True, bg="#15161a", bands=[(0.1, 0.24, "#3f8fbf")],
         author_span=(0.1, 0.24), author_fg="#101216", title_fg="#b9c4cc", title_font="bebas", title_span=(0.32, 0.8), title_scale=0.66,
         rules=[(0.05, 0.056, "#3f8fbf"), (0.9, 0.906, "#3f8fbf")]),
    dict(w=0.066, h=0.25, d=0.17, title="ATLAS SHRUGGED", author="AYN|RAND", upright=True, bg="#121212", fg=GOLD, author_span=(0.06, 0.16),
         title_font="gothic", title_span=(0.24, 0.84), title_scale=0.5, rules=[(0.2, 0.203, GOLD), (0.9, 0.903, GOLD)]),
    dict(case="lewis", colour="#b5302a", label="", books=[
        _lewis("MIRACLES", "#d98a2b"), _lewis("THE SCREWTAPE LETTERS", "#d23b34"), _lewis("MERE CHRISTIANITY", "#1d1d1d"),
        _lewis("THE FOUR LOVES", "#2a8fa6"), _lewis("THE GREAT DIVORCE", "#c93a3a")]),
    dict(w=0.042, h=0.175, d=0.11, title="THE FOUNTAINHEAD", author="AYN RAND", bg="#0f0f10", fg="#f2f0ea", title_font="gothic", author_font="gothic",
         title_scale=0.6, author_scale=0.5, title_span=(0.06, 0.6), author_span=(0.66, 0.94)),
    dict(w=0.03, h=0.2, d=0.14, title="THE SECOND MOUNTAIN", author="DAVID BROOKS", bg="#1f4fa8", author_first=True, author_fg="#ffffff",
         author_font="oswald-b", author_span=(0.06, 0.4), author_align="l", author_scale=0.5, title_fg="#f2d24b", title_font="oswald-b",
         title_span=(0.44, 0.94), title_scale=0.4),
    dict(w=0.03, h=0.21, d=0.14, title="THE 7 HABITS OF HIGHLY EFFECTIVE PEOPLE", author="Stephen R. Covey", bg="#1d3f8a", fg="#ffffff",
         title_font="oswald", author_font="oswald", title_scale=0.42, author_scale=0.34, title_span=(0.05, 0.7), author_span=(0.74, 0.95)),
    dict(w=0.022, h=0.215, d=0.14, title="The Watchmaker", bg="#0c0c0c", fg="#e8e6e0", title_font="garamond", title_span=(0.3, 0.7),
         title_scale=0.62, title_spacing=0.12),
]

# The books from the list, in the next bay.
LIST_SHELF = [
    dict(w=0.058, h=0.24, d=0.165, title="ELON MUSK", author="WALTER ISAACSON", bg="#0d0d0d", fg="#f4f2ec", title_font="gothic", author_font="oswald",
         title_scale=0.62, author_scale=0.2, title_span=(0.08, 0.56), author_span=(0.62, 0.93)),
    dict(w=0.055, h=0.24, d=0.165, title="Steve Jobs", author="WALTER ISAACSON", bg="#f5f5f2", fg="#141414", title_font="baskerville-b", author_font="oswald",
         title_scale=0.42, author_scale=0.2, title_span=(0.08, 0.56), author_span=(0.62, 0.93)),
    dict(w=0.05, h=0.235, d=0.16, title="Benjamin Franklin", author="WALTER ISAACSON", bg="#27344f", fg=GOLD, title_font="playfair-b", author_font="oswald",
         title_scale=0.36, author_scale=0.2, title_span=(0.08, 0.6), author_span=(0.66, 0.93), rules=[(0.04, 0.044, GOLD), (0.956, 0.96, GOLD)]),
    dict(w=0.06, h=0.21, d=0.14, title="ANNA KARENINA", author="LEO TOLSTOY", bg="#7a1f2b", fg=GOLD, title_font="playfair-b", author_font="playfair",
         title_scale=0.3, author_scale=0.2, title_span=(0.1, 0.6), author_span=(0.66, 0.9), rules=[(0.05, 0.054, GOLD), (0.946, 0.95, GOLD)]),
    dict(w=0.036, h=0.235, d=0.16, title="SHOE DOG", author="PHIL KNIGHT", bg="#f4f2ec", fg="#141414", bands=[(0.0, 0.06, "#e8632a")], title_font="gothic",
         author_font="oswald", title_scale=0.8, author_scale=0.32, title_span=(0.1, 0.5), author_span=(0.58, 0.93)),
    dict(w=0.026, h=0.215, d=0.14, title="PIRANESI", author="SUSANNA CLARKE", bg="#151515", fg="#c98a4b", title_font="cinzel-b", author_font="cinzel",
         title_scale=0.5, author_scale=0.3, title_span=(0.08, 0.5), author_span=(0.58, 0.93), title_spacing=0.08),
    dict(w=0.026, h=0.215, d=0.14, title="THERE IS NO ANTIMEMETICS DIVISION", author="QNTM", bg="#e9e9e6", fg="#111111", bands=[(0.86, 1, "#111111")],
         title_font="oswald-b", author_font="oswald-b", author_fg="#e9e9e6", title_scale=0.42, author_scale=0.4, title_span=(0.05, 0.82),
         author_span=(0.88, 0.98)),
    dict(w=0.022, h=0.195, d=0.13, title="The Picture of Dorian Gray", author="OSCAR WILDE", bg="#1f3d36", fg=CREAM, title_font="playfair-i",
         author_font="oswald", title_scale=0.5, author_scale=0.34, title_span=(0.06, 0.66), author_span=(0.7, 0.94)),
    dict(w=0.022, h=0.19, d=0.13, title="Flowers for Algernon", author="DANIEL KEYES", bg="#e7dfc8", fg="#3a2a1a", title_font="playfair-b",
         author_font="oswald", title_scale=0.48, author_scale=0.32, title_span=(0.06, 0.64), author_span=(0.68, 0.94)),
    dict(w=0.024, h=0.175, d=0.11, title="THE COLOR OF MAGIC", author="TERRY PRATCHETT", bg="#5b2a86", fg="#f2d24b", title_font="gothic",
         author_font="oswald", author_fg="#ffffff", title_scale=0.66, author_scale=0.34, title_span=(0.06, 0.58), author_span=(0.62, 0.95)),
    dict(w=0.018, h=0.19, d=0.13, title="GATHERING BLUE", author="LOIS LOWRY", bg="#2d5d8f", fg=CREAM, title_font="oswald-b", author_font="oswald",
         title_scale=0.56, author_scale=0.44, title_span=(0.06, 0.56), author_span=(0.62, 0.94)),
    dict(w=0.013, h=0.18, d=0.11, title="THE COMMUNIST MANIFESTO", author="MARX & ENGELS", bg="#b3201e", fg=CREAM, title_font="gothic",
         author_font="gothic", title_scale=0.7, author_scale=0.6, title_span=(0.05, 0.62), author_span=(0.66, 0.95)),
]

BIG_SHORT = dict(w=0.036, h=0.24, d=0.16, title="THE BIG SHORT", author="MICHAEL LEWIS", bg="#1a1a19", author_first=True, author_fg="#f0eee8",
                 author_font="oswald", author_span=(0.08, 0.46), author_align="l", author_scale=0.4, title_fg="#6ea852", title_font="oswald-b",
                 title_span=(0.5, 0.92), title_scale=0.4)


# ----------------------------------------------------------------------------- books Caleb has read
# Titles and authors from Caleb's reading journal, in the order he read them. Only titles and authors are used.
# Each spine is an original typographic design that suggests the edition; none copies cover art or publisher marks.
# w, h, d: thickness, height, depth in metres at real size. The shelf scales them up so the spines can be read.
HC, TP, MM = (0.24, 0.16), (0.21, 0.14), (0.178, 0.108)     # hardcover, trade paperback, mass-market (height, depth)


def _b(title, author, w, size, bg, fg, tf="garamond-b", af="garamond", **kw):
    h, d = size
    spec = dict(w=w, h=h, d=d, title=title, author=author.upper() if af in ("oswald", "oswald-b", "gothic", "bebas", "cinzel") else author,
                bg=bg, fg=fg, title_font=tf, author_font=af)
    spec.setdefault("title_scale", 0.56)
    spec.setdefault("author_scale", 0.36)
    spec.update(kw)
    return spec


def _sanderson(title, w, bg, accent):
    return _b(title, "Brandon Sanderson", w, HC, bg, CREAM, "cinzel-b", "cinzel", title_fg=accent, title_scale=0.44, author_scale=0.3,
              title_span=(0.08, 0.62), author_span=(0.68, 0.94), rules=[(0.04, 0.043, accent), (0.957, 0.96, accent)])


def _trisolaris(title, w, bg):
    return _b(title, "Cixin Liu", w, TP, bg, "#e9e2cf", "oswald", "oswald", title_scale=0.5, author_scale=0.34, title_spacing=0.06,
              bands=[(0.0, 0.05, "#c23a2a")], title_span=(0.1, 0.66))


def _foundation(title, w, bg):
    return _b(title, "Isaac Asimov", w, MM, bg, "#f2d24b", "bebas", "oswald", author_fg="#f4f2ec", title_scale=0.62, author_scale=0.34,
              title_span=(0.06, 0.64), author_span=(0.68, 0.95))


def _ranger(title, w, bg):
    return _b(title, "John Flanagan", w, TP, bg, "#e8dcc0", "cinzel-b", "garamond", title_scale=0.42, author_scale=0.34,
              author_first=True, author_span=(0.05, 0.3), author_align="l", title_span=(0.36, 0.95),
              bands=[(0.0, 0.035, "#2f4a2a"), (0.965, 1.0, "#2f4a2a")])


def _discworld(title, w):
    return _b(title, "Terry Pratchett", w, MM, "#4a2a7a", "#f2d24b", "gothic", "oswald", author_fg="#ffffff", title_scale=0.7,
              author_scale=0.34, title_span=(0.06, 0.6), author_span=(0.64, 0.95))


def _christie(title, w, bg):
    return _b(title, "Agatha Christie", w, MM, bg, "#f4f2ec", "playfair-b", "oswald", title_scale=0.46, author_scale=0.3,
              author_first=True, author_span=(0.05, 0.36), author_align="l", title_span=(0.4, 0.95), author_fg="#e2b13c")


def _isaacson(title, w, bg, fg, tf="gothic", ts=0.6):
    return _b(title, "Walter Isaacson", w, HC, bg, fg, tf, "oswald", title_scale=ts, author_scale=0.2,
              title_span=(0.08, 0.58), author_span=(0.64, 0.93))


def _rand(title, w, size, bg, fg, ts=0.5):
    return _b(title, "Ayn Rand", w, size, bg, fg, "gothic", "gothic", title_scale=ts, author_scale=0.42,
              title_span=(0.06, 0.66), author_span=(0.72, 0.94))


READ = [
    _b("Thinking, Fast and Slow", "Daniel Kahneman", 0.04, TP, "#f3f1ea", "#1c1c1c", "baskerville", "oswald", title_fg="#c7342a", title_scale=0.4, author_scale=0.3),
    _b("The 7 Habits of Highly Effective People", "Stephen R. Covey", 0.03, TP, "#1d3f8a", "#ffffff", "oswald", "oswald", title_scale=0.38, author_scale=0.3, title_span=(0.05, 0.7), author_span=(0.74, 0.95)),
    _b("CAN'T HURT ME", "David Goggins", 0.034, HC, "#111111", "#f4f2ec", "gothic", "gothic", title_fg="#e2c44a", title_scale=0.72, author_scale=0.5),
    _sanderson("Tress of the Emerald Sea", 0.04, "#0f4a3c", "#d9b45a"),
    _sanderson("The Sunlit Man", 0.036, "#7a2a14", "#f0b04a"),
    _b("SAPIENS", "Yuval Noah Harari", 0.04, TP, "#f2efe6", "#1c1c1c", "gothic", "oswald", bands=[(0.08, 0.14, "#d2452c")], title_span=(0.18, 0.6), title_scale=0.66),
    _b("Gilead", "Marilynne Robinson", 0.026, TP, "#9db3c4", "#1d2a38", "playfair-i", "garamond", title_scale=0.56, author_scale=0.34),
    _b("MERE CHRISTIANITY", "C·S· LEWIS", 0.022, TP, "#f3f0e6", "#1d1d1d", "cinzel", "cinzel", author_first=True,
         author_span=(0.02, 0.19), author_fg="#ffffff", author_align="l", author_scale=0.36, bands=[(0, 0.21, "#1d1d1d"), (0.92, 1, "#1d1d1d")],
         title_span=(0.26, 0.88), title_scale=0.4, title_spacing=0.05),
    _sanderson("Yumi and the Nightmare Painter", 0.042, "#1b2240", "#e86aa8"),
    _trisolaris("THE THREE-BODY PROBLEM", 0.032, "#1a1a1a"),
    _b("We Are Legion (We Are Bob)", "Dennis E. Taylor", 0.026, TP, "#0d2a4a", "#9fd3f0", "oswald-b", "oswald", author_fg="#ffffff", title_scale=0.4, author_scale=0.3),
    _b("The Count of Monte Cristo", "DUMAS", 0.062, MM, "#111111", "#f1ede2", "playfair-i", "oswald", bands=[(0.8, 0.86, "#efece2")],
       author_first=True, author_span=(0.07, 0.2), author_fg="#e2622a", author_align="l", author_scale=0.18, title_span=(0.24, 0.76), title_scale=0.26),
    _b("ATOMIC HABITS", "James Clear", 0.03, HC, "#f4f2ec", "#1c1c1c", "oswald-b", "oswald", bands=[(0.05, 0.08, "#e0a71e")], title_scale=0.5, author_scale=0.3),
    _b("TOO BIG TO FAIL", "Andrew Ross Sorkin", 0.045, TP, "#e8e4d8", "#111111", "gothic", "oswald", title_fg="#b0201c", title_scale=0.66, author_scale=0.3),
    _b("HILLBILLY ELEGY", "J.D. Vance", 0.028, TP, "#f2eee2", "#1f2a44", "oswald-b", "oswald", title_scale=0.5, author_scale=0.34),
    _sanderson("Wind and Truth", 0.07, "#0e2a52", "#e8c46a"),
    _discworld("THE COLOR OF MAGIC", 0.024),
    _discworld("THE LIGHT FANTASTIC", 0.024),
    _discworld("EQUAL RITES", 0.022),
    _b("The Power of Consistency", "Weldon Long", 0.026, HC, "#2a3f6a", "#f4f2ec", "baskerville-b", "oswald", title_scale=0.36, author_scale=0.3),
    _christie("Murder on the Links", 0.02, "#1d3a3a"),
    _christie("And Then There Were None", 0.02, "#2a1414"),
    _b("BORN TO RUN", "Christopher McDougall", 0.03, TP, "#e8a63a", "#1c1c1c", "gothic", "oswald", title_scale=0.72, author_scale=0.3),
    _b("PROJECT HAIL MARY", "Andy Weir", 0.04, HC, "#0d1a2e", "#f2c44a", "oswald-b", "oswald", author_fg="#ffffff", title_scale=0.5, author_scale=0.32),
    _b("Source Code", "Bill Gates", 0.038, HC, "#f4f2ec", "#1c1c1c", "baskerville-b", "oswald", bands=[(0.0, 0.04, "#2f6fd6")], title_scale=0.5, author_scale=0.32),
    _b("The Princess Bride", "William Goldman", 0.032, TP, "#6a1a2a", "#f2d9a0", "playfair-b", "garamond", title_scale=0.46, author_scale=0.34),
    _b("The Walk", "Richard Paul Evans", 0.026, HC, "#c9d6dc", "#22313a", "playfair", "garamond", title_scale=0.5, author_scale=0.34),
    _ranger("The Ruins of Gorlan", 0.03, "#4a3a24"),
    _ranger("The Burning Bridge", 0.03, "#5a2a1c"),
    _ranger("The Siege of Macindaw", 0.03, "#2a3a4a"),
    _ranger("The Emperor of Nihon-Ja", 0.032, "#3a2a3a"),
    _b("DUNE", "Frank Herbert", 0.05, TP, "#c97a2a", "#2a1a10", "cinzel-b", "cinzel", title_scale=0.6, author_scale=0.3, title_spacing=0.2, title_align="m", title_span=(0.1, 0.6)),
    _b("DUNE MESSIAH", "Frank Herbert", 0.03, TP, "#8a3a1c", "#f2d9a0", "cinzel-b", "cinzel", title_scale=0.5, author_scale=0.3, title_spacing=0.08),
    _b("Edenbrooke", "Julianne Donaldson", 0.028, TP, "#e6d6e2", "#4a2a4a", "playfair-i", "garamond", title_scale=0.54, author_scale=0.34),
    _trisolaris("THE DARK FOREST", 0.042, "#0f1a2a"),
    _trisolaris("DEATH'S END", 0.05, "#2a2f36"),
    _foundation("FOUNDATION", 0.02, "#1a3a5a"),
    _foundation("FOUNDATION AND EMPIRE", 0.02, "#3a1a4a"),
    _foundation("SECOND FOUNDATION", 0.02, "#4a1a1a"),
    _foundation("FOUNDATION'S EDGE", 0.024, "#1a4a3a"),
    _b("WILD SWANS", "Jung Chang", 0.05, TP, "#f2ede2", "#1c1c1c", "cinzel-b", "garamond", title_fg="#b0201c", title_scale=0.5, author_scale=0.34),
    _b("ON CHINA", "Henry Kissinger", 0.05, TP, "#b3201e", "#f4e7c4", "cinzel-b", "oswald", title_scale=0.56, author_scale=0.3),
    _b("The Rise of Theodore Roosevelt", "Edmund Morris", 0.055, TP, "#1d2b44", "#d9b45a", "baskerville-b", "oswald", title_scale=0.34, author_scale=0.26),
    _b("The 7½ Deaths of Evelyn Hardcastle", "Stuart Turton", 0.036, TP, "#121212", "#d9b45a", "playfair-b", "oswald", title_scale=0.4, author_scale=0.3),
    _b("Strange the Dreamer", "Laini Taylor", 0.042, TP, "#2a5a8a", "#f2e6c0", "playfair-i", "garamond", title_scale=0.5, author_scale=0.34),
    _b("All the Light We Cannot See", "Anthony Doerr", 0.042, TP, "#2a4a7a", "#f2d24b", "baskerville", "garamond", author_fg="#f4f2ec", title_scale=0.4, author_scale=0.32),
    _b("Let My People Go Surfing", "Yvon Chouinard", 0.03, TP, "#f2ede2", "#1d3a5a", "oswald-b", "oswald", title_scale=0.42, author_scale=0.3),
    _b("THE CHRONICLES OF NARNIA", "C.S. Lewis", 0.075, TP, "#6a1f1c", "#e8c46a", "cinzel-b", "cinzel", title_scale=0.36, author_scale=0.3, rules=[(0.05, 0.054, "#e8c46a"), (0.946, 0.95, "#e8c46a")]),
    _b("A Wrinkle in Time", "Madeleine L'Engle", 0.02, MM, "#2a2a5a", "#f2d24b", "playfair-b", "garamond", author_fg="#ffffff", title_scale=0.5, author_scale=0.34),
    _b("Alcatraz Versus the Evil Librarians", "Brandon Sanderson", 0.026, TP, "#f2c41e", "#1c1c1c", "oswald-b", "oswald", title_scale=0.38, author_scale=0.3),
    _isaacson("Steve Jobs", 0.055, "#f5f5f2", "#141414", "baskerville-b", 0.4),
    _b("FRANKENSTEIN", "Mary Shelley", 0.024, MM, "#1d1d1d", "#d8d4c8", "cinzel-b", "garamond", title_scale=0.5, author_scale=0.36, title_spacing=0.06),
    _b("THE CHOSEN", "POTOK", 0.026, MM, "#8d8d8b", "#111111", "gothic", "gothic", title_scale=0.6, author_scale=0.6, title_span=(0.3, 0.62), author_span=(0.68, 0.9)),
    _b("JUST MERCY", "Bryan Stevenson", 0.03, TP, "#f2ede2", "#1c1c1c", "oswald-b", "oswald", bands=[(0.0, 0.05, "#2a4a7a")], title_scale=0.56, author_scale=0.32),
    _b("The Coddling of the American Mind", "Lukianoff & Haidt", 0.03, TP, "#e8e4d8", "#1c1c1c", "oswald", "oswald", title_fg="#c7342a", title_scale=0.4, author_scale=0.28),
    _b("DEEP WORK", "CAL NEWPORT", 0.03, HC, "#f2c81e", "#111111", "gothic", "gothic", title_scale=0.86, author_scale=0.7, title_span=(0.04, 0.5), author_span=(0.52, 0.88)),
    _b("1776", "David McCullough", 0.042, TP, "#1d2a44", "#f2ede2", "baskerville-b", "oswald", title_fg="#c7342a", title_scale=0.66, author_scale=0.3),
    _sanderson("Tailored Realities", 0.03, "#3a1a3a", "#d9b45a"),
    _b("THERE IS NO ANTIMEMETICS DIVISION", "QNTM", 0.026, TP, "#e9e9e6", "#111111", "oswald-b", "oswald-b", bands=[(0.86, 1, "#111111")], author_fg="#e9e9e6",
       title_scale=0.42, author_scale=0.4, title_span=(0.05, 0.82), author_span=(0.88, 0.98)),
    _isaacson("Benjamin Franklin", 0.05, "#27344f", GOLD, "playfair-b", 0.36),
    _isaacson("ELON MUSK", 0.058, "#0d0d0d", "#f4f2ec", "gothic", 0.62),
    _rand("ATLAS SHRUGGED", 0.066, HC, "#121212", GOLD, 0.5),
    _rand("THE FOUNTAINHEAD", 0.046, MM, "#0f0f10", "#f2f0ea", 0.6),
    _b("PIRANESI", "SUSANNA CLARKE", 0.026, TP, "#151515", "#c98a4b", "cinzel-b", "cinzel", title_scale=0.5, author_scale=0.3, title_spacing=0.08),
    _b("GATHERING BLUE", "LOIS LOWRY", 0.02, TP, "#2d5d8f", CREAM, "oswald-b", "oswald", title_scale=0.56, author_scale=0.44),
    _b("Flowers for Algernon", "DANIEL KEYES", 0.024, TP, "#e7dfc8", "#3a2a1a", "playfair-b", "oswald", title_scale=0.48, author_scale=0.32),
    _b("THE COMMUNIST MANIFESTO", "MARX & ENGELS", 0.014, MM, "#b3201e", CREAM, "gothic", "gothic", title_scale=0.7, author_scale=0.6),
    _b("Blue Like Jazz", "Donald Miller", 0.026, TP, "#3a6aa6", "#f4f2ec", "playfair-i", "garamond", title_scale=0.54, author_scale=0.34),
    _b("ANNA KARENINA", "LEO TOLSTOY", 0.07, TP, "#7a1f2b", GOLD, "playfair-b", "playfair", title_scale=0.3, author_scale=0.2, rules=[(0.05, 0.054, GOLD), (0.946, 0.95, GOLD)]),
    _b("The Picture of Dorian Gray", "OSCAR WILDE", 0.022, TP, "#1f3d36", CREAM, "playfair-i", "oswald", title_scale=0.5, author_scale=0.34),
    _b("A Short Stay in Hell", "Steven L. Peck", 0.014, TP, "#d9d2c0", "#1c1c1c", "garamond-i", "garamond", title_scale=0.6, author_scale=0.42),
    _b("Harry Potter and the Methods of Rationality", "Eliezer Yudkowsky", 0.06, TP, "#2a2a2a", "#e8c46a", "garamond-b", "garamond", title_scale=0.3, author_scale=0.24),
    _b("SHOE DOG", "PHIL KNIGHT", 0.036, HC, "#f4f2ec", "#141414", "gothic", "oswald", bands=[(0.0, 0.06, "#e8632a")], title_scale=0.8, author_scale=0.32, title_span=(0.1, 0.5), author_span=(0.58, 0.93)),
    _rand("ANTHEM", 0.012, MM, "#2a2a2a", "#e8e4d8", 0.6),
    _b("The Paper Menagerie", "Ken Liu", 0.036, TP, "#f2ede2", "#2a2a2a", "playfair", "garamond", bands=[(0.06, 0.1, "#c7342a")], title_scale=0.5, author_scale=0.34),
    _b("IF ANYONE BUILDS IT, EVERYONE DIES", "YUDKOWSKY & SOARES", 0.03, HC, "#111111", "#f4f2ec", "oswald-b", "oswald", title_fg="#e8632a",
       title_scale=0.42, author_scale=0.28, title_span=(0.05, 0.7), author_span=(0.74, 0.96)),
]
