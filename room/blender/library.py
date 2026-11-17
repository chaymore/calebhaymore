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
