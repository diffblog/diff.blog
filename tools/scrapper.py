from googlesearch import search 

template = """
"{}": [
    "{}",
    []
],"""
with open("raw.txt") as f:
    lines = f.readlines()

for line in lines:
    loc = line.find("http://")
    if loc == -1:
        loc = line.find("https://")
    
    full_name = line[:loc - 1]
    blog_url = line[loc: -1]
    for url in search("{} github".format(full_name), stop=1):
        if not "github.com" in url:
            continue
        
        loc = url.find("github.com")
        github_username = url[loc + 11: ]
        print(template.format(github_username, blog_url))
        break
