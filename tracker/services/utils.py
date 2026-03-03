def hitung_konsistensi(total, selesai):
 if total == 0:
  return 0
 return int((selesai / total) * 100)

def hitung_scale(max_value):
 step = 5

 if max_value <= 20:
  y_max = 20
 else:
  import math
  y_max = math.ceil(max_value / step) * step

 return y_max, step