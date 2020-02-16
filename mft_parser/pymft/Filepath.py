'''
file path GG~
'''
class Filepath():
    def __init__(self, parent, record_id, name):
        self.parent = parent
        self.record_id = record_id
        self.name = name
    '''
    structure = [ 
        ["ATTR_TYPE", 0, 4],
    ]
    '''
data = [ #parent, I, name?
    [0, 5, "ROOT"],
    [5, 6, "A"],
    [5, 7, "B"],
    [6, 8, "C"],
    [7, 9, "D"],
    [7, 10, "E"],
    [7, 11, "F"],
    [10, 12, "G"], # resident['PARENT_DIRECTORY_FILE_RECORD_NUMBER'][1]  # FILENAME
]

files = {}
for d in data:
    files[d[1]] = Filepath(parent=d[0], record_id=d[1], name=d[2])

dest = [10, 12, "G"]
parent = dest[1]
path = []
while True:
    if parent == 0: break # Root 인 경우 break
    path.append(files[parent].name)
    parent = files[parent].parent
path = "/".join(path[-1::-1])
print(path)