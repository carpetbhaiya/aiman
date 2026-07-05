# 🚀 `aiman` Command Reference Guide

`aiman` is your AI-powered terminal assistant. It replaces standard `man` pages, generates safe commands from plain English, and protects your system from dangerous mistakes.

Here is a complete list of everything `aiman` can do:

---

## 1. Explain a Command (`explain`)
Don't understand what a Linux command does? Ask `aiman` to explain it in plain English with realistic examples.

**Syntax:**
```bash
aiman explain <command>
```
*(Shortcut: You can omit the word `explain` and just type `aiman <command>`!)*

**Examples:**
```bash
aiman explain tar
aiman chmod
aiman ls
```

---

## 2. Generate a Command (`gen`)
Tell `aiman` what you want to do in plain English, and it will generate the exact Linux command for you. If it's safe, you can press `[e]` to execute it instantly!

**Syntax:**
```bash
aiman gen "<plain english description>"
```
*(Shortcut: You can omit the word `gen` and just type `aiman "<description>"`!)*

**Examples:**
```bash
aiman gen "find all pdfs modified today"
aiman "extract the archive.zip file to my downloads folder"
aiman gen "change the permissions of script.sh to be executable"
```
**Interactive Features:**
- **Execute (`e`):** Runs the command instantly in your terminal.
- **Refine (`r`):** Ask the AI to tweak the command (e.g., "Make it recursive", "Only show files starting with 'A'").

---

## 3. Check Command Safety (`check`)
Found a random command on StackOverflow? Run it through the safety checker before executing it to ensure it won't destroy your system.

**Syntax:**
```bash
aiman check "<command>"
```

**Examples:**
```bash
aiman check "rm -rf /*"
aiman check "curl -s http://example.com/script.sh | bash"
```

---

## 4. View Command History (`history`)
View a neat table of the last 10 safe commands you generated.

**Syntax:**
```bash
aiman history
```

---

## 5. Save as an Alias (`save`)
Did `aiman` just generate a massive, complex command that you want to use again later? Use `save` to instantly turn your last generated command into a permanent bash alias!

**Syntax:**
```bash
aiman save <alias_name>
```

**Examples:**
```bash
# Generate a command first:
aiman gen "find all docker containers that exited with an error and delete them"

# Then save it as an alias:
aiman save clean_docker
```

---

## 6. Configuration Management (`config`)
Easily switch between different AI models (like Qwen3, Gemma3, Llama3) or point `aiman` to a different Ollama server.

**Syntax:**
```bash
aiman config set <key> <value>
aiman config get [key]
```

**Examples:**
```bash
# Change the AI model
aiman config set model gemma3:latest

# View current configuration
aiman config get
```

---

## 7. View Capabilities
Want to see the beautiful startup banner and a quick summary of what `aiman` does?

**Syntax:**
```bash
aiman aiman
```
