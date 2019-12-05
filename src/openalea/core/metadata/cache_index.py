# Cache index : { vid: time/ cost to get} - if vid in index -> cache exist

class Cache_item():
    def __init__(self, vid=None, size=0, site=None):
        self.vid = vid
        self.size = size
        self.site = site

    def __repr__(self):
        return "Cache item - vid : " + str(self.vid) + " | size : " + str(self.size) + " | site : " + str(self.site)


class Cache_index():
    def __init__(self):
        self.cache_index = dict()

    def add_cache_index_item(self, item):
        self.cache_index[item.vid] = item

    def add_cache_index_itemlist(self, items):
        for item in items:
            self.cache_index[item.vid] = item

    def generate_fake(self):
        list_items = []
        item1 = Cache_item(vid="2", size=100, site="s2")
        item2 = Cache_item(vid="5", size=50000, site="s1")

        list_items.append(item1)
        list_items.append(item2)

        self.add_cache_index_itemlist(list_items)

    def check_index(self, vid):
        if vid in self.cache_index:
            return self.cache_index[vid]
        else:
            return None