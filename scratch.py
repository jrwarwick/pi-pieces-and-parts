import re

line="one* two| three"

datafieldsRegEx = re.compile('[\t:\*|│]+')

fields = datafieldsRegEx.split(line)

print(len(fields))
print(fields)
for field in fields:
    print(field.strip())