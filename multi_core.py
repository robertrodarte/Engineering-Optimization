"""
Prelminary multi-core implementation
Turned into hand-verification implementation
"""
from instance import hand_verified_instance
from model import build_model, report

# Hand verified instances
instance = hand_verified_instance()
model, x, start, y = build_model(instance)
model.solve()
report(model, instance, x, start)