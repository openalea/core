from random import choice
from string import ascii_letters


# sites:
class Site():
    def __init__(self, sid="", compute_cost=0., storage_cost=0., compute_power=0., buzyness=0.):
        if not sid:
            sid = ''.join(choice(ascii_letters) for i in range(12))
        self.sid = sid
        self.compute_cost = compute_cost
        self.compute_power = compute_power
        self.storage_cost = storage_cost
        self.buzyness = buzyness

        self.transfer_cost = dict()
        self.transfer_cost[self.sid] = 0.
        # list task id, whose input data is on the site
        self.input_storage = set()

    def __repr__(self):
        return "Site - sid : " + str(self.sid) + " | compute_cost : " + str(self.compute_cost) \
               + " | storage_cost : " + str(self.storage_cost) + " | buzyness : " + str(self.buzyness) \
               + " | input data : " + str(self.input_storage) + " | transfer : " + str(self.transfer_cost)

    def free(self):
        self.buzyness = 0

    def increase_workload(self, inc=0):
        self.buzyness += inc

    def add_transfer_site(self, nsite_sid, t_cost):
        self.transfer_cost[nsite_sid] = t_cost

    def add_input_data(self, vid):
        self.input_storage.add(vid)

    def check_input(self, vid):
        return vid in self.input_storage


def link_two_sites(site1, site2, transfer_cost):
    site1.add_transfer_site(site2.sid, transfer_cost)
    site2.add_transfer_site(site1.sid, transfer_cost)


class MultiSiteCloud():
    def __init__(self, list_sites=dict()):
        self.list_sites = list_sites

    def add_site(self, site):
        self.list_sites[site.sid] = site

    def add_sitelist(self, sites):
        for site in sites:
            self.list_sites[site.sid] = site

    def generate_fake(self):
        # start 3 sites
        list_items = []
        site1 = Site(sid='s0', compute_cost=10., storage_cost=10., compute_power=10.)
        site2 = Site(sid='s1', compute_cost=100., storage_cost=1., compute_power=10.)
        site3 = Site(sid='s2', compute_cost=1., storage_cost=100., compute_power=10.)

        list_items.append(site1)
        list_items.append(site2)
        list_items.append(site3)

        self.add_sitelist(list_items)

        # generate transfer cost
        link_two_sites(site1, site2, 2)
        link_two_sites(site1, site3, 4)
        link_two_sites(site3, site2, 6)


