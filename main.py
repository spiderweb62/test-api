import pandas as pd
import random
import logging
import re

from typing import Any, Optional, Set


from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from fastapi_utils.timing import add_timing_middleware

RE = re.compile(
    "TIMING:\s+Wall:\s+(?P<wall>[\d\.]*)ms\s+\|\s+CPU:\s+(?P<cpu>[\d\.]*)ms\s+\|\s+main\.(?P<name>\w*)"
).match

results = []


def record(message):
    global results
    res = RE(message)
    results.append(res.groupdict())
    print(results)


app = FastAPI()
add_timing_middleware(app, record=record)

df = None


@app.on_event("startup")
@repeat_every(seconds=300)
def generate_numbers() -> None:
    global df
    l = [random.randint(2, 5) for i in range(random.randint(1000000, 10000000))]
    df = pd.DataFrame({"value": l})


@app.get("/items/")
async def get_items():
    desc = df.value
    return {
        "total": len(desc),
        "min": int(desc.min()),
        "max": int(desc.max()),
        "variance": float(desc.std()),
    }
