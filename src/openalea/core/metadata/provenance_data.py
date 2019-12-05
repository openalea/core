# fake provenance for WF test "add_test"
# 6 vertices
# 3 edges
# input vid = 2 et 4
# output vid = 5
# 0 et 1 = auto input et output "node" - not used
# 4 = add node


class Prov_item():
    def __init__(self, vid=None, exec_time=0, input_size=0, output_size=0):
        self.vid = vid
        self.exec_time = exec_time
        self.input_size = input_size
        self.output_size = output_size

    def __repr__(self):
        return "Provenance item - vid : " + str(self.vid) + " | exec_time : " + str(self.exec_time) + \
               " | input_size : " + str(self.input_size) + " | output_size : " + str(self.output_size)


class Prov():
    def __init__(self):
        self.prov = dict()

    def add_prov_item(self, item):
        self.prov[item.vid] = item

    def add_prov_itemlist(self, items):
        for item in items:
            self.prov[item.vid] = item

    def check_prov(self, vid):
        if vid in self.prov:
            return self.prov[vid]
        else:
            return None

    def generate_fake(self):
        list_items = []
        item1 = Prov_item("2", 10, 5000, 300)
        item2 = Prov_item("4", 3, 200, 1000)
        item3 = Prov_item("5", 5, 1300, 100)

        list_items.append(item1)
        list_items.append(item2)
        list_items.append(item3)

        self.add_prov_itemlist(list_items)