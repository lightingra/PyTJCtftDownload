from tokenize import group
from upgrade import UpGrade, TJCScreen
import re

tjc = TJCScreen()
data = "comok 1,101,TJC4024T032_011R,52,61488,D264B8204F0E1828,16777216\xff\xff\xff"
tjc.parse(data)
print(tjc.device_info)

if __name__ == "__main__":
    pass