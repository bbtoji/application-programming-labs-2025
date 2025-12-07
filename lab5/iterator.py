import csv

class ImageIterator:
    def __init__(self, csv_file: str) -> None:
        self.path_list = []
        with open(csv_file, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                self.path_list.append(row[0])
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index < len(self.path_list):
            self.index += 1
            return self.path_list[self.index - 1]
        else:
            raise StopIteration