class SchedulingPlan():
    def __init__(self):
        self.plan = []
        self.cost = 0.

    def add_to_plan(self, task, site):
        self.plan.append((task, site))

    def add_to_cost(self, new_cost):
        if isinstance(new_cost, float):
            self.cost+=new_cost
        else:
            pass