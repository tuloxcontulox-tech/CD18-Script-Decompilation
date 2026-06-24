import re

with open('Scripts/Players/TailsObject.txt', 'r') as f:
    content = f.read()

# Get all aliases
aliases = set(re.findall(r'player\.\w+', content.split('// Function declarations')[0]))

# Get all usages
usages = set(re.findall(r'player\.\w+', content))

missing = usages - aliases
if missing:
    print("Missing aliases in TailsObject:", missing)
else:
    print("All player aliases accounted for in TailsObject.")

with open('Scripts/Players/PlayerObject.txt', 'r') as f:
    p_content = f.read()

print("if balance in PlayerObject:", p_content.count('if ') - p_content.count('end if'))
