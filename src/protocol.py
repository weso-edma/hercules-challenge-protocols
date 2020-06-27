class Protocol():
    def __init__(self, protocol_id, title, abstract, materials,
                 procedure, equipment, background,
                 categories, authors):
        self.id = protocol_id
        self.title = title
        self.abstract = abstract
        self.materials = materials
        self.procedure = procedure
        self.equipment = equipment
        self.background = background
        self.categories = categories
        self.authors = authors
    
    def to_dict(self):
        return {
            'pr_id': self.id,
            'title': self.title,
            'abstract': self.abstract,
            'materials': '|'.join(self.materials),
            'procedure': '|'.join(self.procedure),
            'equipment': '|'.join(self.equipment),
            'background': self.background,
            'categories': '|'.join(self.categories),
            'authors': '|'.join(self.authors)
        }

