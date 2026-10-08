import os

repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
index_file = os.path.join(repo_dir, "index.html")

with open(index_file, "r", encoding="utf-8") as f:
    content = f.read()

# Dark preview
dark_content = content.replace('id="login-overlay" class="fixed', 'id="login-overlay" class="hidden fixed').replace('id="portal-container" class="hidden', 'id="portal-container" class="')
with open(os.path.join(repo_dir, "scratch", "preview_dark.html"), "w", encoding="utf-8") as f:
    f.write(dark_content)

# Light preview
light_content = dark_content.replace('<html class="dark"', '<html class="light"')
light_content = light_content.replace("localStorage.getItem('nnos_theme') || 'dark'", "'light'")
with open(os.path.join(repo_dir, "scratch", "preview_light.html"), "w", encoding="utf-8") as f:
    f.write(light_content)

print("Previews created successfully!")
