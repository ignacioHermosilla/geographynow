import re
tokens_to_remove = ['(Geography Now!)', 'Geography Now!', '(Flag Friday)', 'Flag Friday!', 'Flag Friday', '(Geography Now)']

pattern = r'\([Gg]eography [Nn]ow\)'
num = re.sub(pattern, '', 'hola') 
