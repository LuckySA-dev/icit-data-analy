"""Convert generate_slide_graphs.py from dark theme to white theme"""

with open('generate_slide_graphs.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    # COLORS dict central values
    ("'bg': '#1a1a2e'", "'bg': '#FFFFFF'"),
    ("'text': '#FFFFFF'", "'text': '#333333'"),
    ("'grid': '#333355'", "'grid': '#CCCCCC'"),
    # Text colors (white -> dark)
    ("color='white'", "color='#333333'"),
    # Edge colors
    ("edgecolor='white'", "edgecolor='#CCCCCC'"),
    ("edgecolors='white'", "edgecolors='#666666'"),
    # Tick params
    ("colors='white'", "colors='#333333'"),
    # Legend label colors
    ("labelcolor='white'", "labelcolor='#333333'"),
    # Text props in pie charts
    ("'color': 'white'", "'color': '#333333'"),
    # Summary box dark facecolors -> light tints
    ("facecolor='#2a0000'", "facecolor='#FFE0E0'"),
    ("facecolor='#2a1500'", "facecolor='#FFF3E0'"),
    ("facecolor='#001a2e'", "facecolor='#E0F7FA'"),
    # Cyan -> dark blue (for white bg visibility)
    ("color='cyan'", "color='#0277BD'"),
    ("edgecolor='cyan'", "edgecolor='#0277BD'"),
    ("colors='cyan'", "colors='#0277BD'"),
    (".set_color('cyan')", ".set_color('#0277BD')"),
    # Lime -> dark green
    ("color='lime'", "color='#2E7D32'"),
    # Yellow quadrant label -> dark goldenrod (unreadable on white)
    ("color='yellow'", "color='#B8860B'"),
]

count = 0
for old, new in replacements:
    n = content.count(old)
    if n > 0:
        content = content.replace(old, new)
        count += n
        print(f'  Replaced {n}x: {repr(old)} -> {repr(new)}')
    else:
        print(f'  (0 matches): {repr(old)}')

with open('generate_slide_graphs.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nTotal replacements: {count}')
print('White theme applied successfully!')
