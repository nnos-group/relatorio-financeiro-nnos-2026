import re

files = ['lider.html', 'matriz.html', 'uva.html', 'booking.html', 'prospeccao.html']

for fname in files:
    with open(fname, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"=== {fname} ===")
    # find all max-w
    max_w = set(re.findall(r'max-w-\[[^\]]+\]', text))
    print("max-w-[...]:", max_w)
    
    # check .wrap in style
    wraps = re.findall(r'\.wrap\s*\{[^}]+\}', text)
    if wraps:
        print("CSS .wrap:", wraps)
    
    # check header, nav, main container
    for tag in ['header', 'nav', 'main', 'footer']:
        matches = re.findall(rf'<{tag}[^>]*>', text)
        if matches:
            print(f"  {tag}: {matches[0][:120]}")
    
    # find inner container div in header or main
    inner_divs = re.findall(r'<div class="([^"]*max-w-[^"]*)"', text)
    print("  inner max-w divs count:", len(inner_divs))
    if inner_divs:
        print("  sample inner divs:", inner_divs[:3])
