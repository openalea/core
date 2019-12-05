# function to get the site and minimal cost for a task, with prov + sites
def minimum_cost_site(vid, provenance, multisites):
    vid = str(vid)
    # if no provenance data for task vid -> NOT TAKEN INTO ACCOUNT
    # TODO: manage if no prov data -> average? best site? random? ....
    if vid not in provenance.prov:
        print("Not enough provenance information on task: " + str(vid))
        return None, None

    # find the sites where the input data exist:
    input_site = []
    for s in multisites.list_sites:
        if multisites.list_sites[s].check_input(vid):
            input_site.append(s)
    # IF No site has the input data -> cannot be computed
    if not input_site:
        print('Input data not found')
        return None, None

    possible_cost = dict()
    # for each site get the cost
    for s1 in multisites.list_sites:
        # if the Input data is not on s1 -> get the minimal cost to transfer the intput data to the site:
        min_transfer_cost = []
        for s2 in input_site:
            transfer_cost = multisites.list_sites[s1].transfer_cost[s2]
            # get the input data size | here from provenance, in real cases the scheduler knows it
            input_data_size = provenance.prov[vid].input_size

            get_input_cost_tmp = transfer_cost * input_data_size
            min_transfer_cost.append(get_input_cost_tmp)
        get_input_cost = min(min_transfer_cost)

        # the cost to compute the task on this site:
        compute_cost = multisites.list_sites[s1].compute_cost * provenance.prov[vid].exec_time

        total_cost = get_input_cost + compute_cost
        #     print s1, "total_cost : " ,total_cost, 'get_input_cost : ', get_input_cost, 'compute_cost', compute_cost

        possible_cost[s1] = total_cost

    best_site = min(possible_cost)
    best_cost = possible_cost[best_site]

    return best_site, best_cost