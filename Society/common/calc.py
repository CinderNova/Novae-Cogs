import random, datetime, math, asyncio, time, discord
import numpy as np
start_time = datetime.datetime.now()


class Calculation():
    
    def probability():
        " Returns a number within [0,1]. "
        random_seed = random.randint(1, 10**16)
        random.seed(a=random_seed)
        random_list = [random.uniform(0,1) for i in range(0,16)]
        return random.choice(random_list)
    
    def wage(income: int, offset: int):
        " Returns a wage [int] within [median - offset, median + offset] that is normal-distributed."
        wage = round(random.uniform(income - offset, income + offset))
        return wage
    
    def scalar_product(v: list, w: list):
        v = np.array(v)
        w = np.array(w)
        try:
            return np.dot(v,w)
        except ValueError:
            return -1

    def norm(v: list):
        v = np.array(v)
        return math.sqrt(np.dot(v,v))

    def time_diff(start_time: datetime, end_time: datetime):
        """ Difference between two datetimes in hours """
        t = start_time
        T = end_time
        delta = abs(T-t)
        return math.ceil(delta.total_seconds() / 3600.0)
    
    def bonuses(user: discord.User):
        "hi"
        


def calc_bonus(job_bonus: float, marriage_bonuses: list, house_bonuses: list, marriages: list, houses: list, booster: float):
    m = scalar_product(marriages, marriage_bonuses)
    h = scalar_product(houses, house_bonuses)
        
    if m==0 or m <0:
        m = 1
    else:
        if m>12.5:
            m = 12
        else:
            pass
    if h == 0 or h<1:
        h = 1
    else:
        if h > 50:
            h = 50
        else:
            pass
    general_bonus = 1.15*job_bonus*booster*(h+m)/2
    return general_bonus
    
def get_month(month_num: int):
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ]
    return months[month_num-1]



