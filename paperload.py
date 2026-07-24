from jinja2 import Environment, FileSystemLoader
import json

with open("generated_biology_paper.json", "r", encoding="utf-8") as f:
    paper = json.load(f)

env = Environment(loader=FileSystemLoader("."))
template = env.get_template("template.html")
html_content = template.render(paper=paper)

with open("generated_biology_paper.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML saved")