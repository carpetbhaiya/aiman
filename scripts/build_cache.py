import urllib.request
import zipfile
import io
import json
import os
import re

def parse_tldr_page(cmd_name: str, raw_md: str) -> str:
    lines = raw_md.split('\n')
    description = ""
    examples = []
    
    current_example_desc = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith(">"):
            if not description and not line.lower().startswith("> more info"):
                description = line.lstrip(">").strip()
        elif line.startswith("-"):
            current_example_desc = line.lstrip("-").strip()
        elif line.startswith("`") and current_example_desc:
            # We found a command example
            cmd_example = line.strip("`")
            examples.append(f"{current_example_desc}\n   `{cmd_example}`")
            current_example_desc = ""

    out = f"**`{cmd_name}`**: {description}\n\n**Examples:**\n"
    for i, ex in enumerate(examples, 1):
        out += f"{i}. {ex}\n"
        
    return out.strip()


def main():
    url = "https://github.com/tldr-pages/tldr/archive/main.zip"
    print(f"Downloading {url}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            zip_data = response.read()
    except Exception as e:
        print(f"Error downloading: {e}")
        return

    print("Extracting and parsing...")
    commands = {}
    with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
        for filename in z.namelist():
            # The github archive has a top-level dir, e.g., tldr-main/
            if ("/pages/linux/" in filename or "/pages/common/" in filename) and filename.endswith(".md"):
                cmd_name = os.path.basename(filename)[:-3]
                raw_md = z.read(filename).decode("utf-8")
                
                parsed_content = parse_tldr_page(cmd_name, raw_md)
                commands[cmd_name] = parsed_content

    out_file = os.path.join(os.path.dirname(__file__), "..", "aiman", "core", "command_cache.json")
    print(f"Saving {len(commands)} commands to {out_file}...")
    with open(out_file, "w") as f:
        json.dump(commands, f, indent=2)
    print("Done!")

if __name__ == "__main__":
    main()
