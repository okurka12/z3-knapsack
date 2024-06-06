from z3 import *


class ObjectArithRefs:
    """container for z3 ArithRef's regarding an individual Object"""

    def __init__(self, t: ArithRef, w: ArithRef, p: ArithRef) -> None:
        """
        `t` - taken - integer 0 or 1
        `w` - weight - integer
        `p` - price - integer
        """
        self.t = t
        self.w = w
        self.p = p

class Object:
    """an object to fit in knapsack"""

    def __init__(self, n: int, weight: int, profit: int) -> None:
        self.n = n
        self.weight = weight
        self.profit = profit

    def addRefs(self, t: ArithRef, w: ArithRef, p: ArithRef) -> None:
        """add z3 ArithRefs"""

        # z3 arithrefs regarding individual object
        self.ar = ObjectArithRefs(t, w, p)

    def __repr__(self) -> str:
        return f"Object"


# an instance of the knapsack problem
# p01 from:
# https://people.sc.fsu.edu/~jburkardt/datasets/knapsack_01/knapsack_01.html
KNAPSACK_CAPACITY = 165
OBJECTS = [
    Object( 1, 23, 92),
    Object( 2, 31, 57),
    Object( 3, 29, 49),
    Object( 4, 44, 68),
    Object( 5, 53, 60),
    Object( 6, 38, 43),
    Object( 7, 63, 67),
    Object( 8, 85, 84),
    Object( 9, 89, 87),
    Object(10, 82, 72)
]

# initialize solver
s = Solver()

# construct ArithRefs for the objects
for obj in OBJECTS:
    wn = Int(f"w{obj.n}")
    pn = Int(f"p{obj.n}")
    on = Int(f"o{obj.n}")
    obj.addRefs(on, wn, pn)

    s.add(wn == obj.weight)
    s.add(pn == obj.profit)

    # print(type(pn == obj.profit))  # <class 'z3.z3.BoolRef'>

    s.add(Or(on == 0, on == 1))


# print(type(object_taken[0]))  # <class 'z3.z3.ArithRef'>

################################################################################
# define the knapsack capacity
################################################################################
c = Int("c")
s.add(c == KNAPSACK_CAPACITY)

################################################################################
# constraint the sum of taken objects
################################################################################
object_weight_sum = Sum(*[o.ar.t * o.ar.w for o in OBJECTS])
s.add(object_weight_sum <= c)

################################################################################
# assert that the price of the taken objects is maximal
################################################################################
alternative_ts = []  # list of ats (at - alternative taken)
alternative_bools = []  # BoolRefs that all ats are 0 or 1
alternative_price = []  # prices of the objects times if they're taken
alternative_weight = []  # weigths of the objects times if they're taken
for obj in OBJECTS:
    atn = Int(f"at{obj.n}")
    alternative_ts.append(atn)
    alternative_bools.append(Or(atn == 0, atn == 1))
    alternative_price.append(atn * obj.ar.p)
    alternative_weight.append(atn * obj.ar.w)

object_price_sum = Sum(*[o.ar.p * o.ar.t for o in OBJECTS])
alternative_price_sum = Sum(*alternative_price)
alternative_weight_sum = Sum(*alternative_weight)
alt_sum_greater = alternative_price_sum > object_price_sum
formula_body = And(
    alternative_weight_sum <= c,
    alt_sum_greater,
    *alternative_bools
)
s.add(Not(Exists(alternative_ts, formula_body)))
# s.add(Exists(alternative_ts, And(alt_sum_greater, *alternative_bools)))

################################################################################
# add informative variables
################################################################################
knapsack_cap = Int("o_knapsack_capacity")
total_weight = Int("total_weight")
total_price = Int("total_price")
s.add(total_weight == object_weight_sum)
s.add(total_price == object_price_sum)
s.add(knapsack_cap == c)









print(s.check())
try:
    print(s.model())
except Z3Exception:
    print("model couldn't be printed")
